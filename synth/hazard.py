from synth.function import BooleanFunction, minterm_to_cube, literal_count, cube_covers
from synth.qm import merge, PI, minimize_sop, minimize_pos


def adjacent(minterms, n):
    
    """ Example: adjacent([0, 1, 2, 3], 2) returns [(0, 1, '-0'), (0, 2, '0-'), (1, 3, '1-'), (2, 3, '-1')] """

    ms = sorted(minterms)
    result = []
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            cube = merge(minterm_to_cube(ms[i], n), minterm_to_cube(ms[j], n))
            if cube is not None:
                result.append((ms[i], ms[j], cube))
    return result


def is_covered(a, b, cubes):
    """True if any cube in cubes covers minterm a and b"""
    for c in cubes:
        if cube_covers(c, a) and cube_covers(c, b):
            return True
    return False

def uncovered_pairs(minterms, cubes, n):
    """Return a list of pairs of minterms that are not covered by any cube in cubes."""
    result = []
    for a, b, cube in adjacent(minterms, n):
        if not is_covered(a, b, cubes):
           result.append((a, b, cube))   
    return result

def find_hazardSOP(f):
    n = len(f.var_names)
    sop = minimize_sop(f)
    return uncovered_pairs(f.on_set, sop, n)

def find_hazardPOS(f):
    n = len(f.var_names)
    pos = minimize_pos(f)
    return uncovered_pairs(f.off_set(), pos, n)


"""I use AI here"""
def add_covers(minterms, cubes, primes, n):
    """Example (F = AB + A'C):
    add_cover_terms([1, 3, 6, 7], ['0-1', '11-'], ['0-1', '11-', '-11'], 3) -> ['-11', '0-1', '11-']"""

    result = list(cubes)
    for a, b, cube in adjacent(minterms, n):
        if not is_covered(a, b, result):
            for p in primes:
                if cube_covers(p, a) and cube_covers(p, b):
                    result.append(p)
                    break
    return sorted(result)


def hazard_free_sop(f):
    n = len(f.var_names)
    sop = minimize_sop(f)
    primes = PI(f)
    return add_covers(f.on_set, sop, primes, n)

"""I use AI here"""
def hazard_free_pos(f):
    n = len(f.var_names)
    f_bar = BooleanFunction(f.var_names, f.off_set(), f.dc_set)
    pos = minimize_pos(f)
    primes = PI(f_bar)
    return add_covers(f.off_set(), pos, primes, n)


"""I use AI here"""
def describe_hazard(hazard, var_names):
    """(3, 7, '-11'), [A, B, C] -> "A changes while B=1, C=1  (m3 <-> m7)" """
    a, b, cube = hazard
    changing = ""
    fixed = []
    for i in range(len(cube)):
        if cube[i] == "-":
            changing = var_names[i]
        else:
            fixed.append(var_names[i] + "=" + cube[i])
 
    text = changing + " changes"
    if len(fixed) > 0:
        text += " while " + ", ".join(fixed)
    return text + "  (m" + str(a) + " <-> m" + str(b) + ")"

