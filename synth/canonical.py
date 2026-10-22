from synth.function import minterm_to_cube, sop_to_string, pos_to_string

# 1. Canonical SOP for F (when terms F = 1)
def canonicalsop(f):
    n = len(f.var_names)

    binarylist = []
    for m in sorted(f.on_set):
        binarylist.append(minterm_to_cube(m, n))

    return sop_to_string(binarylist, f.var_names)


# 2. Canonical POS for F (terms F = 0)
def canonicalpos(f):
    n = len(f.var_names)

    binarylist = []
    for m in sorted(f.off_set()):
        binarylist.append(minterm_to_cube(m, n))

    return pos_to_string(binarylist, f.var_names)

# 3. Inverse Canonical SOP (when F' = 1)
def inversecanonicalsop(f):
    n = len(f.var_names)

    binarylist = []
    for m in sorted(f.off_set()):
        binarylist.append(minterm_to_cube(m, n))

    return sop_to_string(binarylist, f.var_names)

# 4. Inverse Canonical POS (when F' = 0)
def inversecanonicalpos(f):
    n = len(f.var_names)

    binarylist = []
    for m in sorted(f.on_set):
        binarylist.append(minterm_to_cube(m, n))

    return pos_to_string(binarylist, f.var_names)

from synth.function import BooleanFunction

if __name__ == "__main__":
    f = BooleanFunction(
        var_names=["A", "B", "C"],
        on_set={2, 3, 5, 7},
        output_name="F"
    )

    print("Canonical SOP:", canonicalsop(f))
    print("Canonical POS:", canonicalpos(f))
    print("Inverse SOP:", inversecanonicalsop(f))
    print("Inverse POS:", inversecanonicalpos(f))