#!/bin/env python3

from abc import ABC, abstractmethod
from argparse import ArgumentParser
from collections import defaultdict
from functools import wraps
from pathlib import Path
from subprocess import run
from typing import Callable
from os import geteuid, getlogin, getuid, seteuid
from contextlib import AbstractContextManager


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


class AddFlatpakRepositories(Step):
    """Add flatpak repositories"""

    def run(self) -> None:
        flatpak_repos_file_path = Path(__file__).parent / "flatpak-repos.txt"
        with flatpak_repos_file_path.open("r", encoding="utf-8") as file:
            for line in file:
                name, url = line.split()
                run(["flatpak", "remote-add", "--if-not-exists", name, url])


class InstallAllFlatpakPackages(Step):
    """Install all packages from flatpak"""

    def run(self) -> None:
        flatpak_file_path = Path(__file__).parent / "flatpak-full.txt"
        with flatpak_file_path.open("r", encoding="utf-8") as file:
            refs_per_repo: dict[str, list[str]] = defaultdict(list[str])
            for line in file:
                repo, ref = line.split()
                refs_per_repo[repo].append(ref)
            for repo, refs in refs_per_repo.items():
                run(["flatpak", "install", "--noninteractive", repo, *refs])


class InstallMinimalFlatpakPackages(Step):
    """Install only minimal packages from flatpak"""

    def run(self) -> None:
        flatpak_file_path = Path(__file__).parent / "flatpak-minimal.txt"
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
        config_path.copy_into(Path.home())
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
        AddFlatpakRepositories,
        InstallMinimalFlatpakPackages,
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
