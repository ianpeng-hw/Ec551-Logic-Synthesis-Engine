"""
truth_table.py - Generates a truth table for a Boolean function.

"""

from synth.function import minterm_to_cube

# 12. Custom Command #2 - Truth Table
def truthtable(f):

    # gets the number of variables
    n = len(f.var_names)

    # creates the table header
    header = "m | " + " ".join(f.var_names) + f" | {f.output_name}"
    lines = [header, "-" * len(header)]

    # generates every possible input combination
    for m in range(2 ** n):

        # where we convert the minterm to binary
        binary = minterm_to_cube(m, n)

        # determine the function's output
        if m in f.on_set:
            output = "1"
        elif m in f.dc_set:
            output = "X"
        else:
            output = "0"

        # add a row to the truth table
        row = f"{m} | " + " ".join(binary) + f" | {output}"
        lines.append(row)

    return "\n".join(lines)