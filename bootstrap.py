#!/bin/env python3

# ruff: noqa: PLW1510

from abc import ABC, abstractmethod
from argparse import ArgumentParser
from collections import defaultdict
from collections.abc import Callable
from functools import wraps
from os import getlogin
from pathlib import Path
from subprocess import run


def handle_keyboard_interrupt(original_function) -> Callable:
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        try:
            original_function(*args, **kwargs)
        except KeyboardInterrupt:
            print("\nInterrupted by user")

    return wrapper


class Step(ABC):
    """Base class for all steps of the bootstrap script"""

    __rank: int
    __total: int

    def __init__(self, rank: int, total: int) -> None:
        self.__rank = rank
        self.__total = total
        super().__init__()

    def get_description(self) -> str:
        """
        Method that returns a description of the step.
        By default, uses the docstring of the class.
        """
        doc = self.__class__.__doc__
        return doc.strip() if doc is not None else "No description available."

    def _get_is_enabled_prompt(self) -> str:
        return f"[{self.__rank}/{self.__total}] {self.get_description()} (y/n) "

    def is_enabled(self) -> bool:
        return input(self._get_is_enabled_prompt()).lower().strip() == "y"

    @abstractmethod
    def run(self) -> None:
        """Run the step."""


class InstallPrerequisites(Step):
    """Install prerequisites for the bootstrap script"""

    def run(self) -> None:
        run(["sudo", "pacman", "-S", "--noconfirm", "yay", "flatpak"])


class UpdatePacmanMirrors(Step):
    """Update pacman mirrors to the fastest ones"""

    def run(self) -> None:
        run(["sudo", "pacman-mirrors", "--fasttrack"])
        run(["sudo", "pacman", "-Syy"])


class InstallDistroPackages(Step):
    """Install packages from the distro repositories"""

    def run(self) -> None:
        arch_file_path = Path(__file__).parent / "arch.txt"
        with arch_file_path.open("r", encoding="utf-8") as file:
            run(["sudo", "pacman", "-Syu", "--needed", "--noconfirm", "-"], stdin=file)


class InstallAurPackages(Step):
    """Install packages from the AUR"""

    def run(self) -> None:
        aur_file_path = Path(__file__).parent / "aur.txt"
        with aur_file_path.open("r", encoding="utf-8") as file:
            run(
                [
                    "yay",
                    "-S",
                    "--needed",
                    "--noconfirm",
                    "--norebuild",
                    "--cleanmenu=false",
                    "--diffmenu=false",
                    "--editmenu=false",
                    "--removemake",
                    "--batchinstall",
                    "-",
                ],
                stdin=file,
            )


class AddFlathubRepoForUser(Step):
    """Add flathub repository for the user, removing it for the system if present"""

    def __has_system_remote(self, remote: str) -> bool:
        return (
            remote
            in run(
                ["flatpak", "remotes", "--system", "--columns=name"], text=True
            ).stdout
        )

    def __list_system_apps(self, remote: str) -> list[str]:
        sys_apps_run = run(
            ["flatpak", "list", "--app", "--system", "--columns=application,origin"],
            check=True,
            text=True,
        )
        sys_items = [
            tuple(item.split("\t", maxsplit=1))  # -
            for item in sys_apps_run.stdout
        ]
        sys_apps = [app for app, app_remote in sys_items if app_remote == remote]
        return sys_apps

    def run(self) -> None:

        name = "flathub"
        url = "https://flathub.org/repo/flathub.flatpakrepo"
        migrated_apps = list[str]()

        # Check if flathub is present in system repos
        has_system_flathub = self.__has_system_remote(remote=name)
        if has_system_flathub:
            print("System-wide flathub detected, will be migrated to user.")
            migrated_apps = self.__list_system_apps(remote=name)
            print(f"{len(migrated_apps)} apps will be migrated.")
            run(["flatpak", "remote-delete", "--system", "--force", name])

        # Add user flathub
        run(["flatpak", "--user", "remote-add", "--if-not-exists", name, url])

        # Migrate system apps
        if len(migrated_apps) > 0:
            print("Migrating system flathub apps to user flathub")
            run(
                [
                    "flatpak",
                    "install",
                    "--user",
                    "--noninteractive",
                    name,
                    *migrated_apps,
                ]
            )


class InstallAllFlatpakPackages(Step):
    """Install all packages from flatpak"""

    def run(self) -> None:
        flatpak_file_path = Path(__file__).parent / "flatpak.txt"
        with flatpak_file_path.open("r", encoding="utf-8") as file:
            refs_per_repo: dict[str, list[str]] = defaultdict(list[str])
            for line in file:
                repo, ref = line.split()
                refs_per_repo[repo].append(ref)
            for repo, refs in refs_per_repo.items():
                run(["flatpak", "install", "--noninteractive", repo, *refs])


class SetZshAsDefaultShell(Step):
    """Set zsh as the default shell"""

    def run(self) -> None:
        run(["sudo", "pacman", "-S", "--needed", "--noconfirm", "zsh"])
        run(["chsh", "-s", "/bin/zsh"])
        print("Please logout and login again to apply the changes.")


class SetupShell(Step):
    """Setup zsh goodies"""

    def run(self) -> None:

        # Oh-my-zsh
        run(
            'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
            shell=True,
        )

        # Autosuggestions
        # https://github.com/zsh-users/zsh-autosuggestions/blob/master/INSTALL.md#oh-my-zsh
        run(
            "git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions",
            shell=True,
        )

        # Syntax highlighting
        # https://github.com/zsh-users/zsh-syntax-highlighting/blob/master/INSTALL.md#oh-my-zsh
        run(
            "git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting",
            shell=True,
        )

        # Install a patched nerd font
        # Note: Assumes oh-my-posh is installed.
        run(["oh-my-posh", "font", "install", "meslo"], check=False)

        # Install the shell defaults
        config_file_name = "zsh-config.sh"
        config_path = Path(__file__).parent / config_file_name
        config_path.copy_into(Path.home())  # type: ignore
        zshrc_path = Path.home() / ".zshrc"
        with zshrc_path.open("a", encoding="utf-8") as file:
            file.write(f'\nsource "$HOME/{config_file_name}"\n')


class InstallOpenTabletDriver(Step):
    """Setup OpenTabletDriver for graphics tablet support"""

    def run(self) -> None:
        # Install OpenTabletDriver from AUR
        run(["yay", "-S", "--needed", "--noconfirm", "opentabletdriver"])
        # Enable and start the service
        run(["systemctl", "--user", "enable", "--now", "opentabletdriver"])


class InstallDdcutil(Step):
    """Setup ddcutil for monitor brightness control"""

    def run(self) -> None:
        # Install ddcutil
        run(["sudo", "pacman", "-S", "--needed", "--noconfirm", "ddcutil"])
        # Install udev rules
        run(["sudo", "cp", "/etc/udev/rules.d/60-ddcutil-i2c.rules", "/etc/udev/rules.d"])
        # Create i2c group and add current user to it
        run(["sudo", "groupadd", "--system", "i2c"])
        run(["sudo", "usermod", getlogin(), "-aG", "i2c"])
        # load i2c-dev automatically
        with open("/etc/modules-load.d/i2c.conf", "a") as file:
            file.write("i2c-dev\n")
        print("Please reboot for changes to take effect.")


class InstallSdkman(Step):
    """Setup sdkman to manage JDK versions"""

    def run(self) -> None:
        # Install zip (needed by the installer)
        run(["sudo", "pacman", "-S", "--needed", "--noconfirm", "zip"])
        # Install sdkman
        run('curl -s "https://get.sdkman.io" | bash')


@handle_keyboard_interrupt
def main() -> None:
    """Main function of the bootstrap script."""

    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="If specified, do not actually run the steps.",
    )
    args = parser.parse_args()

    print("Welcome to Geoffrey's bootstrap script")
    print("This script is made to work on Arch linux and its derivatives.")

    # Run steps
    all_steps_classes: list[type[Step]] = [
        UpdatePacmanMirrors,
        InstallDistroPackages,
        InstallAurPackages,
        AddFlathubRepoForUser,
        InstallAllFlatpakPackages,
        InstallOpenTabletDriver,
        InstallDdcutil,
        InstallSdkman,
        SetZshAsDefaultShell,
        SetupShell,
    ]
    all_steps = (
        step_cls(rank=i + 1, total=len(all_steps_classes))
        for i, step_cls in enumerate(all_steps_classes)
    )
    enabled_steps = []
    for step in all_steps:
        if step.is_enabled():
            enabled_steps.append(step)
    for step in enabled_steps:
        print(f"\n### {step.get_description()} ###\n")
        if not args.dry_run:
            step.run()


if __name__ == "__main__":
    main()
