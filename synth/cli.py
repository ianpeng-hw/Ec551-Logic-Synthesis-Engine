"""
cli.py - Interactive command-line shell.

PLACEHOLDER: this minimal version only exists so that main.py runs.
It will be replaced by the full command set (load, sop, pos, minsop, ...,
verilog) once the operations are written.

"""

from __future__ import annotations


def run(initial_file: str | None = None) -> None:
    """Read commands from the user until 'quit'."""
    print("EC551 Logic Synthesis Engine - type 'help' for commands, 'quit' to exit.")
    if initial_file:
        print(f"(Loading files is not implemented yet: {initial_file})")

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue

        command = line.split()[0].lower()
        if command in ("quit", "exit"):
            break
        elif command == "help":
            print("Commands: help, quit  (more coming soon)")
        else:
            print(f"Unknown command: {command}. Type 'help' to see the commands.")