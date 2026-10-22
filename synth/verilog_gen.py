"""
verilog_gen.py - Generate structural Verilog from minimized SOP.

"""

from pathlib import Path
from synth.qm import minimize_sop

def generate_verilog(f, filepath="fpga/generated_logic.v"):

    # gets the minimized SOP cubes
    cubes = minimize_sop(f)

    if cubes is None:
        raise ValueError("SOP minimization did not return a result.")

    variables = f.var_names
    output = f.output_name

    if not variables:
        raise ValueError("Expected at least one input variable.")

    if output in variables:
        raise ValueError("Output name conflicts with an input variable.")

    if any(len(cube) != len(variables) or
           any(bit not in "01-" for bit in cube) for cube in cubes):
        raise ValueError("Invalid SOP cube returned by the minimizer.")

    # this creates the Verilog module
    lines = [
        f"module structurallogic({', '.join(variables + [output])});",
        f"    input {', '.join(variables)};",
        f"    output {output};",
    ]

    # this handles a function that is always 0
    if not cubes:
        lines.append(f"    buf ({output}, 1'b0);")

    # this handles a function that is always 1
    elif "-" * len(variables) in cubes:
        lines.append(f"    buf ({output}, 1'b1);")

    else:
        # this finds which inputs need NOT gates
        inverted = [
            variable
            for i, variable in enumerate(variables)
            if any(cube[i] == "0" for cube in cubes)
        ]

        # creates wires for each product term
        term_wires = [f"term_{i}" for i in range(len(cubes))]

        all_wires = [f"not_{v}" for v in inverted] + term_wires

        lines.append(f"    wire {', '.join(all_wires)};")

        # generates NOT gates
        for variable in inverted:
            lines.append(f"    not (not_{variable}, {variable});")

        # generates the product terms using AND gates
        for i, cube in enumerate(cubes):
            gate_inputs = []

            for j, bit in enumerate(cube):

                if bit == "1":
                    gate_inputs.append(variables[j])

                elif bit == "0":
                    gate_inputs.append(f"not_{variables[j]}")

                # A dash means this variable is omitted

            # single-literal term
            if len(gate_inputs) == 1:
                lines.append(f"    buf (term_{i}, {gate_inputs[0]});")

            # product term with multiple literals
            else:
                lines.append(
                    f"    and (term_{i}, {', '.join(gate_inputs)});"
                )

        # combines all product terms with an OR gate
        if len(term_wires) == 1:
            lines.append(f"    buf ({output}, {term_wires[0]});")
        else:
            lines.append(
                f"    or ({output}, {', '.join(term_wires)});"
            )

    lines.append("endmodule")

    # combines all Verilog lines into a string
    verilog_text = "\n".join(lines) + "\n"

    # saves the generated Verilog file
    target = Path(filepath)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(verilog_text, encoding="utf-8")

    return target
