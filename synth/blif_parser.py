"""
blif_parser.py - Read a BLIF file into a BooleanFunction.


"""

from synth.function import BooleanFunction, minterm_to_cube


def clean_lines(text):
    """Remove comments and blank lines, and join lines that end in a backslash."""
    lines = []
    current = ""
    for line in text.split("\n"):
        # everything after '#' is a comment
        if "#" in line:
            line = line[:line.index("#")]
        line = line.strip()

        # a line ending in '\' continues on the next line
        if line.endswith("\\"):
            current += line[:-1] + " "
            continue

        current += line
        if current.strip() != "":
            lines.append(current.strip())
        current = ""
    return lines


def parse_blif(text):
    """BLIF text -> BooleanFunction."""
    inputs = []
    outputs = []
    gates = []     # one dictionary per .names block

    for line in clean_lines(text):
        parts = line.split()

        if parts[0] == ".model":
            pass                        # the name is not needed here
        elif parts[0] == ".inputs":
            inputs += parts[1:]
        elif parts[0] == ".outputs":
            outputs += parts[1:]
        elif parts[0] == ".names":
            # last name is the gate's output, the others are its inputs
            gate = {"inputs": parts[1:-1], "output": parts[-1], "rows": []}
            gates.append(gate)
        elif parts[0] == ".end":
            break
        elif parts[0].startswith("."):
            raise ValueError("Unsupported BLIF command: " + parts[0])
        else:
            # a truth-table row of the most recent .names block
            if len(gates) == 0:
                raise ValueError("Row is not inside a .names block: " + line)
            gate = gates[-1]

            if len(parts) == 1:
                pattern = ""            # constant gate: ".names X" then "1"
                value = parts[0]
            else:
                pattern = parts[0]
                value = parts[1]

            if value != "1":
                raise ValueError("Only rows ending in 1 are supported: " + line)
            if len(pattern) != len(gate["inputs"]):
                raise ValueError("Row has the wrong number of inputs: " + line)
            gate["rows"].append(pattern)

    if len(outputs) != 1:
        raise ValueError("Exactly one output is supported, found " + str(len(outputs)))
    output = outputs[0]

    # try every input combination; where the output is 1 goes into the ON-set
    on_set = set()
    for m in range(2 ** len(inputs)):
        if simulate(m, inputs, gates, output) == 1:
            on_set.add(m)

    return BooleanFunction(inputs, on_set, output_name=output)


def simulate(m, inputs, gates, output):
    """Value (0 or 1) of the output when the inputs are set to minterm m."""
    values = {}

    # 1. set the primary inputs from the bits of m (inputs[0] is the MSB)
    bits = minterm_to_cube(m, len(inputs))
    for i in range(len(inputs)):
        values[inputs[i]] = int(bits[i])

    # 2. compute gates until the output is known.
    #    A gate can be computed once all of its inputs have values.
    #    Gates may appear in any order in the file, so we keep looping.
    while output not in values:
        progress = False
        for gate in gates:
            if gate["output"] in values:
                continue

            ready = True
            for name in gate["inputs"]:
                if name not in values:
                    ready = False

            if ready:
                values[gate["output"]] = evaluate_gate(gate, values)
                progress = True

        if not progress:
            raise ValueError("Cannot compute " + output + ": a signal is missing or there is a loop")

    return values[output]


def evaluate_gate(gate, values):
    """1 if any row of the gate's truth table matches the current input values."""
    for pattern in gate["rows"]:
        match = True
        for i in range(len(pattern)):
            name = gate["inputs"][i]
            if pattern[i] != "-" and int(pattern[i]) != values[name]:
                match = False
        if match:
            return 1
    return 0


def read_blif(filename):
    """Open a .blif file and return its BooleanFunction."""
    with open(filename) as file:
        text = file.read()
    return parse_blif(text)
