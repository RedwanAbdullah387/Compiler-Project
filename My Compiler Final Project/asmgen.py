# ===== asmgen.py =====
"""
Convert TAC into a simple assembly-like language: MOV, OUT, JMP, JZ/JNZ, RET, labels.
"""

def tac_to_asm(tac_lines):
    asm = []
    for line in tac_lines:
        line = line.strip()
        if not line: continue
        if line.startswith("label "):
            asm.append(line.replace("label ", "").strip() + ":")
        elif line.startswith("PRINT "):
            asm.append("OUT " + line.split("PRINT",1)[1].strip())
        elif line.startswith("IFZ "):
            # IFZ X GOTO L2  -> CMPZ X; JZ L2
            parts = line.split()
            if len(parts) >= 4 and parts[2] == "GOTO":
                asm.append(f"CMPZ {parts[1]}")
                asm.append(f"JZ {parts[3]}")
        elif line.startswith("IF "):
            # IF cond GOTO L1 -> CMP cond; JNZ L1
            parts = line.split()
            if len(parts) >= 4 and parts[2] == "GOTO":
                asm.append(f"CMP {parts[1]}")
                asm.append(f"JNZ {parts[3]}")
        elif line.startswith("GOTO "):
            asm.append("JMP " + line.split()[1])
        elif line.startswith("RETURN "):
            asm.append("RET " + line.split()[1])
        elif line.endswith(":" ):
            asm.append(line)
        elif "=" in line:
            # e.g., a = T1 or T1 = 3 or T2 = a + b
            asm.append("MOV " + line)
        else:
            asm.append("; UNKNOWN: " + line)
    return asm


if __name__ == "__main__":
    import sys
    from lexical import tokenize
    from parser import Parser
    from codegen import TACGen
    from optimizer import optimize
    if len(sys.argv) < 2:
        print("Usage: python3 asmgen.py sample.src"); sys.exit(1)
    src = open(sys.argv[1]).read()
    toks = list(tokenize(src)); tree = Parser(toks).parse()
    g = TACGen(); tac = g.gen(tree)
    opt = optimize(tac)
    asm = tac_to_asm(opt)
    print("===== ASSEMBLY CODE =====")
    for line in asm: print(line)
    print("=========================\n")
