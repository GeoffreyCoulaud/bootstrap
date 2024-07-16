#!/bin/env python3

from abc import ABC, abstractmethod
from argparse import ArgumentParser
from functools import wraps
from subprocess import run
from typing import Callable, Iterable


class Step(ABC):
    """Base class for all steps of the bootstrap script"""

    __rank: int
    __total: int

    def __init__(self, rank: int, total: int) -> None:
        self.__rank = rank
        self.__total = total
        super().__init__()

    @abstractmethod
    def get_description(self) -> str:
        """Method that returns a description of the step."""

    def _get_is_enabled_prompt(self) -> str:
        return f"[{self.__rank}/{self.__total}] {self.get_description()} (y/n) "

    def is_enabled(self) -> bool:
        return input(self._get_is_enabled_prompt()).lower().strip() == "y"

    @abstractmethod
    def run(self) -> None:
        """Run the step."""


class InstallPrerequisites(Step):

    def get_description(self) -> str:
        return "Install prerequisites"

    def run(self) -> None:
        run(["sudo", "pacman", "-S", "--noconfirm", "yay", "flatpak"])


class UpdatePacmanMirrors(Step):

    def get_description(self) -> str:
        return "Update pacman mirrors"

    def run(self) -> None:
        run(["sudo", "pacman-mirrors", "--fasttrack"])
        run(["sudo", "pacman", "-Syy"])


class InstallDistroPackages(Step):

    def get_description(self) -> str:
        return "Install packages from repos"

    def run(self) -> None:
        with open("arch.txt", "r", encoding="utf-8") as file:
            run(["sudo", "pacman", "-Syu", "--noconfirm", "-"], stdin=file)


class InstallAurPackages(Step):

    def get_description(self) -> str:
        return "Install packages from the AUR"

    def run(self) -> None:
        with open("aur.txt", "r", encoding="utf-8") as file:
            run(
                [
                    "yay",
                    "-S",
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

    def get_description(self) -> str:
        return "Install flatpak repositories"

    def run(self) -> None:
        with open("flatpak-repos.txt", "r", encoding="utf-8") as file:
            for line in file:
                name, url = line.split()
                run(["flatpak", "remote-add", "--if-not-exists", name, url])


class InstallFlatpakPackages(Step):

    def get_description(self) -> str:
        return "Install packages from flatpak"

    def run(self) -> None:
        with open("flatpak.txt", "r", encoding="utf-8") as file:
            refs_per_repo = {}
            for line in file:
                repo, ref = line.split()
                if repo not in refs_per_repo:
                    refs_per_repo[repo] = []
                refs_per_repo[repo].append(ref)
            for repo, refs in refs_per_repo.items():
                run(["flatpak", "install", "--noninteractive", repo, *refs])


class SetZshAsDefaultShell(Step):

    def get_description(self) -> str:
        return "Set zsh as default shell"

    def run(self) -> None:
        run(["sudo", "pacman", "-Syu", "--noconfirm", "zsh"])
        zsh = run(
            ["command", "-v", "zsh"], capture_output=True, text=True
        ).stdout.strip()
        run(["chsh", "-s", zsh])
        print("Please logout and login again to apply the changes.")


def handle_keyboard_interrupt(original_function) -> Callable:
    @wraps(original_function)
    def wrapper(*args, **kwargs):
        try:
            original_function(*args, **kwargs)
        except KeyboardInterrupt:
            print("\nInterrupted by user")

    return wrapper


@handle_keyboard_interrupt
def main() -> None:

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

    all_steps_classes: Iterable[Step] = [
        UpdatePacmanMirrors,
        InstallDistroPackages,
        InstallAurPackages,
        AddFlatpakRepositories,
        InstallFlatpakPackages,
        SetZshAsDefaultShell,
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
