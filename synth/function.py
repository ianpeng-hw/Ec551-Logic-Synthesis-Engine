"""
function.py - Shared data structure for the logic synthesis engine.

Conventions (both of us follow these):

  * var_names[0] is the MOST significant bit.
        ["A", "B", "C"], minterm 6 = 110  ->  A=1, B=1, C=0

  * A cube (product term) is a string of '0', '1', '-', one character
    per variable, in the same order as var_names.
        "0-1"  ->  A'C   (B does not appear)

  * For POS, a cube covers OFF-set minterms: '0' -> X, '1' -> X'.
        "0-0"  ->  (A + C)

  * Never change f.on_set directly. Copy it first:
        remaining = set(f.on_set)

"""


class BooleanFunction:
    def __init__(self, var_names, on_set, dc_set=set(), output_name="F"):
        self.var_names = list(var_names)
        self.on_set = set(on_set)
        self.dc_set = set(dc_set)
        self.output_name = output_name

        # every minterm must fit in the number of variables
        for m in self.on_set | self.dc_set:
            if m < 0 or m >= 2 ** len(self.var_names):
                raise ValueError(f"Minterm {m} is out of range")

    def off_set(self):
        """Minterms where F = 0."""
        result = set()
        for m in range(2 ** len(self.var_names)):
            if m not in self.on_set and m not in self.dc_set:
                result.add(m)
        return result


def minterm_to_cube(minterm, num_vars):
    """(6, 3) -> '110'"""
    return format(minterm, f"0{num_vars}b")


def literal_count(cube):
    """'0-1' -> 2"""
    count = 0
    for c in cube:
        if c != "-":
            count += 1
    return count


def cube_covers(cube, minterm):
    """('0-1', 3) -> True, because 3 = 011"""
    bits = minterm_to_cube(minterm, len(cube))
    for i in range(len(cube)):
        if cube[i] != "-" and cube[i] != bits[i]:
            return False
    return True


def cube_to_product(cube, var_names):
    """'0-1' -> A'C   (all dashes -> 1)"""
    literals = []
    for i in range(len(cube)):
        if cube[i] == "1":
            literals.append(var_names[i])
        elif cube[i] == "0":
            literals.append(var_names[i] + "'")
    if len(literals) == 0:
        return "1"
    return "".join(literals)


def cube_to_sum(cube, var_names):
    """'0-0' -> (A + C)   (all dashes -> 0)"""
    literals = []
    for i in range(len(cube)):
        if cube[i] == "0":
            literals.append(var_names[i])
        elif cube[i] == "1":
            literals.append(var_names[i] + "'")
    if len(literals) == 0:
        return "0"
    return "(" + " + ".join(literals) + ")"


def sop_to_string(cubes, var_names):
    """['0-1', '11-'] -> A'C + AB   (no cubes -> 0)"""
    if len(cubes) == 0:
        return "0"
    terms = []
    for cube in cubes:
        terms.append(cube_to_product(cube, var_names))
    return " + ".join(terms)


def pos_to_string(cubes, var_names):
    """['0-0', '10-'] -> (A + C)(A' + B)   (no cubes -> 1)"""
    if len(cubes) == 0:
        return "1"
    clauses = []
    for cube in cubes:
        clauses.append(cube_to_sum(cube, var_names))
    return "".join(clauses)