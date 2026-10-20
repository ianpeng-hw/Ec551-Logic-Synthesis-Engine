"""
cli.py - Interactive command-line shell.

PLACEHOLDER: this minimal version only exists so that main.py runs.
It will be replaced by the full command set (load, sop, pos, minsop, ...,
verilog) once the operations are written.

"""

from __future__ import annotations

from synth.parasesop import parseexpression, getvariables, minterms
from synth.function import BooleanFunction


def run(initial_file: str | None = None) -> None:
    
    """Read commands from the user until 'quit'."""
    print ("EC551 Logic Synthesis Engine - type 'help' for commands, 'quit' to exit.")

    # This will allow us to enter one expression and run it against multiple commands.
    current_function = None

    if initial_file:
        print (f"(Loading files is not implemented yet: {initial_file})")

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
            print ("Commands: help, quit, sop, pos  (more coming soon)")

        # This is for Sum of Products
        elif command == "sop":
            parts = line.split(maxsplit=1)

            if len(parts) == 1 or not parts[1].strip():
                print("Please enter a Boolean expression.")
            else:
                parts[1] = parts[1].upper()
                expression = parts[1]
                parsedterms = parseexpression(expression)
                variables = getvariables(parsedterms)
                minterm = minterms(parsedterms, variables)

                current_function = BooleanFunction(
                var_names = variables,
                on_set = minterm,
                output_name = "F"
               )

                print("Variables:", current_function.var_names)
                print("ON-set:", sorted(current_function.on_set))
                print("OFF-set:", sorted(current_function.off_set()))

        else:
            print (f"Unknown command: {command}. Type 'help' to see the commands.")


