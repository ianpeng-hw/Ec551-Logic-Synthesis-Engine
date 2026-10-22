from itertools import combinations
from synth.function import BooleanFunction, minterm_to_cube, literal_count, cube_covers

def merge(a, b):
    dif =0
    result = ""
    for i in range(len(a)):
        if a[i] == b[i]:
            result += a[i]
        elif a[i] == '-' or b[i] == '-':
            return None
        else:
            result += '-'
            dif += 1
    if dif == 1:
        return result
    return None

def is_covered(m, cubes):
    """True if any cube in cubes covers minterm m."""
    for c in cubes:
        if cube_covers(c, m):
            return True
    return False

def PI(f):
    primes = set()

    n = len(f.var_names)
    current = set()
    for m in f.on_set | f.dc_set:
        current.add(minterm_to_cube(m, n))
 
    while len(current) > 0:
        next_round = set()
        used = set()
 
        cubes = list(current)
        for i in range(len(cubes)):
            for j in range(i + 1, len(cubes)):
                r = merge(cubes[i], cubes[j])
                if r != None:
                    next_round.add(r)
                    used.add(cubes[i])
                    used.add(cubes[j])
 
        for c in cubes:
            if c not in used:
                primes.add(c)
        current = next_round
 
    result = []
    for p in primes:
        keep = False
        for m in f.on_set:
            if cube_covers(p, m):
                keep = True
        if keep:
            result.append(p)
 
    return sorted(result)

def EPI(f):
    primes = PI(f)
    essentials = set()
 
    for m in f.on_set:        
        count = 0
        last = ""
        for p in primes:
            if cube_covers(p, m):
                count += 1
                last = p
        if count == 1:
            essentials.add(last)
 
    return sorted(essentials)

def total_literals(cubes):
    """Total number of literals in a list of cubes."""
    total = 0
    for c in cubes:
        total += literal_count(c)
    return total

def covers_all(cubes, minterms):
    """True if every minterm is covered by at least one cube."""
    for m in minterms:
        if not is_covered(m, cubes):
            return False
    return True

"""I use AI here"""
def minimize_sop(f):
    if len(f.on_set) == 0:
        return []            # F = 0

    primes = PI(f)
    chosen = EPI(f)

    remaining = []
    for m in f.on_set:
        if not is_covered(m, chosen):
            remaining.append(m)

    if len(remaining) == 0:
        return chosen

    others = []
    for p in primes:
        if p not in chosen:
            for m in remaining:
                if cube_covers(p, m):
                    others.append(p)
                    break

    for size in range(1, len(others) + 1):
        best = None
        for combo in combinations(others, size):
            if covers_all(combo, remaining):
                if best == None or total_literals(combo) < total_literals(best):
                    best = combo
        if best != None:
            return sorted(chosen + list(best))


def minimize_pos(f):
    f_bar = BooleanFunction(f.var_names, f.off_set(), f.dc_set)
    return minimize_sop(f_bar)