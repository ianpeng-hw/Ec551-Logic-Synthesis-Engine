"""
cli.py - Interactive command-line shell.

PLACEHOLDER: this minimal version only exists so that main.py runs.
It will be replaced by the full command set (load, sop, pos, minsop, ...,
verilog) once the operations are written.

"""

from __future__ import annotations

from synth.parasesop import parseexpression, getvariables, minterms
from synth.function import BooleanFunction, sop_to_string, pos_to_string
from synth.canonical import canonicalpos, canonicalsop, inversecanonicalpos, inversecanonicalsop
from synth.truth_table import truthtable
from synth.qm import PI, EPI, minimize_sop, minimize_pos, total_literals 
from synth.hazard import find_hazardSOP, find_hazardPOS, describe_hazard  
from synth.verilog_gen import generate_verilog 

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
            print ("Commands: help, quit, expr, sop, pos, invsop, invpos, offcount, oncount, truth, primeim, essentialpi, minsop, minpos")


       # This is for Boolean input
        elif command == "expr":
            parts = line.split(maxsplit=1)

            # Check if the user entered an expression
            if len(parts) == 1 or not parts[1].strip():
                print("Please enter a Boolean expression.")

            else:
                expression = parts[1].upper()

                # try processing the Boolean expression
                try:
                    parsedterms = parseexpression(expression)
                    variables = getvariables(parsedterms)
                    minterm = minterms(parsedterms, variables)

                    # Store the Boolean function for future commands
                    current_function = BooleanFunction(
                        var_names=variables,
                        on_set=minterm,
                        output_name="F"
                    )

                    print("Variables:", current_function.var_names)
                    print("ON-set:", sorted(current_function.on_set))
                    print("OFF-set:", sorted(current_function.off_set()))
                    print("Prime Implicants:", sop_to_string(PI(current_function), current_function.var_names))
                    print("Essential Prime Implicants:", sop_to_string(EPI(current_function), current_function.var_names))

                          

                # Catch invalid Boolean expressions
                except ValueError as error:
                    print("Error:", error)


        # 1. Canonical SOP
        elif command == "sop":
            if current_function is None:
                print("Please load an expression first using expr.")
            else:
                print("Canonical SOP:", canonicalsop(current_function))


        # 2. Canonical POS
        elif command == "pos":
            if current_function is None:
                print("Please load an expression first using expr.")
            else:
                print("Canonical POS:", canonicalpos(current_function))


        # 3. Inverse Canonical SOP
        elif command == "invsop":
            if current_function is None:
                print("Please load an expression first using expr.")
            else:
                print("Inverse Canonical SOP:", inversecanonicalsop(current_function))


        # 4. Inverse Canonical POS
        elif command == "invpos":
            if current_function is None:
                print("Please load an expression first using expr.")
            else:
                print("Inverse Canonical POS:", inversecanonicalpos(current_function))
        
        # 5. Literal Minimized SOP
        elif command == "minsop":
            if current_function is None:
              print("Please load an expression first using expr.")
            else:

                # gets the minimized binary cubes
                cubes = minimize_sop(current_function)

                # converts the cubes to a Boolean expression
                expression = sop_to_string(cubes, current_function.var_names)

                # counts literals in canonical and minimized SOP
                n = len(current_function.var_names)
                canonical_count = len(current_function.on_set) * n
                minimized_count = total_literals(cubes)

                # calculates the number of literals saved
                saved = canonical_count - minimized_count

                print("Minimized SOP:", expression)
                print("Canonical SOP literals:", canonical_count)
                print("Minimized SOP literals:", minimized_count)
                print("Literals saved:", saved)

        # 6. Literal Minimized SOP
        elif command == "minpos":
            if current_function is None:
              print("Please load an expression first using expr.")
            else:

                # gets the minimized binary cubes
                cubes = minimize_pos(current_function)

                # converts the cubes to a Boolean expression
                expression = pos_to_string(cubes, current_function.var_names)

                # counts literals in canonical and minimized POS
                n = len(current_function.var_names)
                canonical_count = len(current_function.off_set()) * n
                minimized_count = total_literals(cubes)

                # calculates the number of literals saved
                saved = canonical_count - minimized_count

                print("Minimized POS:", expression)
                print("Canonical POS literals:", canonical_count)
                print("Minimized POS literals:", minimized_count)
                print("Literals saved:", saved)

        # 7. Prime Implicant count
        elif command == "primeim":
            if current_function is None:
                print("Please load an expression first using expr.")
            else:
                primes = PI(current_function)
                print("Prime Implicant count:", len(primes))

        # 8. Essential Prime Implicant count
        elif command == "essentialpi":
            if current_function is None:
                print("Please load an expression first using expr.")
            else:
                essentials = EPI(current_function)
                print("Essential Prime Implicant count:", len(essentials))

        # 9. On-set count
        elif command == "oncount":
            if current_function is None:
                print("Please load an expression first using expr.")
            else:
                print("ON-set minterm count:", len(current_function.on_set)) 

        # 10. Off-set count
        elif command == "offcount":
            if current_function is None:
                print("Please load an expression first using expr.")
            else:
                print("OFF-set minterm count:", len(current_function.off_set())) 

        # Used AI for this part        
        # 11. Custom Command #1 - Hazard Detection
        elif command == "hazard":
            if current_function is None:
                print("Please load an expression first using expr.")

            else:
                # finds the hazards in minimized SOP and POS circuits
                sop_hazards = find_hazardSOP(current_function)
                pos_hazards = find_hazardPOS(current_function)

                # displays potential static-1 hazards
                print("SOP Static-1 Hazards:")

            if len(sop_hazards) == 0:
                print("No hazards detected.")
            else:
                for hazard in sop_hazards:
                    print(" ", describe_hazard(hazard, current_function.var_names))

            # displays potential static-0 hazards
            print("POS Static-0 Hazards:")

            if len(pos_hazards) == 0:
                print("No hazards detected.")
            else:
                for hazard in pos_hazards:
                    print(" ", describe_hazard(hazard, current_function.var_names))

        # 12. Custom Command #2 - Truth Table
        elif command == "truth":
            if current_function is None:
                print("Please load an expression first using expr.")
            else:
                print(truthtable(current_function))

        # This is the structural Verilog Generation
        elif command == "verilog":
            if current_function is None:
                print("Please load an expression first using expr.")
            else:
                try:
                    filepath = generate_verilog(current_function)
                    print("Structural Verilog generated:", filepath)
                except (ValueError, OSError) as error:
                    print("Error:", error)

        # Handle unknown commands
        else:
            print(f"Unknown command: {command}. Type 'help' to see the commands.")




