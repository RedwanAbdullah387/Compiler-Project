# ===== optimizer.py =====
"""
Simple optimizer: constant folding and trivial dead code elimination.
"""
import re


def optimize(tac_lines):
    optimized = []
    consts = {}

    for line in tac_lines:
        # constant folding for patterns like T1 = 2 + 3
        m = re.match(r"^(T\d+)\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*([\+\-\*/])\s*([0-9]+(?:\.[0-9]+)?)$", line)
        if m:
            t, a, op, b = m.groups()
            # compute with python safely
            try:
                val = str(eval(f"{a}{op}{b}"))
            except Exception:
                val = None
            if val is not None:
                optimized.append(f"{t} = {val}")
                consts[t] = val
                continue
        # replace known temporaries with constants
        for c, v in consts.items():
            if re.search(rf"\b{c}\b", line):
                line = re.sub(rf"\b{c}\b", v, line)
        optimized.append(line)

    # determine used temps
    used = set()
    for l in optimized:
        for t in re.findall(r"\bT\d+\b", l):
            used.add(t)
    final = []
    for l in optimized:
        m = re.match(r"^(T\d+)\s*=", l)
        if m:
            if m.group(1) in used:
                final.append(l)
        else:
            final.append(l)
    return final


if __name__ == "__main__":
    import sys
    from lexical import tokenize
    from parser import Parser
    from codegen import TACGen
    if len(sys.argv) < 2:
        print("Usage: python3 optimizer.py sample.src"); sys.exit(1)
    src = open(sys.argv[1]).read()
    toks = list(tokenize(src)); tree = Parser(toks).parse()
    g = TACGen(); tac = g.gen(tree)
    print("===== OPTIMIZATION =====\nBefore:")
    for i, line in enumerate(tac, 1): print(f"({i}) {line}")
    opt = optimize(tac)
    print("\nAfter:")
    for i, line in enumerate(opt, 1): print(f"({i}) {line}")
    print("========================\n")
