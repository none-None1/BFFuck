from .bffuck import BFFuck
import argparse, sys


def _cli():
    ap = argparse.ArgumentParser(
        description="BFFuck CLI tool\nMakes Brainfucking Easier!\nEnjoy brainfucking with the tool\nIf you encounter any error, you can post an issue at GitHub."
    )
    ap.add_argument("program", help="BFFuck program file name")
    ap.add_argument(
        "--playfield", "-p", help="Number of bytes for playfield, must be an integer"
    )
    ap.add_argument(
        "--output",
        "-o",
        help="Output brainfuck file name, default is the standard output",
    )
    ap.add_argument("--byte", "-b", help="Use multi-byte integers (1 or 2 or 3 bytes)")
    a = ap.parse_args()
    program = a.program
    with open(program, "r") as f:
        code = f.read()
    playfield = 15
    if a.playfield:
        playfield = int(a.playfield)
    if a.byte:
        byte = int(a.byte)
    try:
        bf = BFFuck(playfield).compile(code, byte=int(a.byte))
    except Exception as err:
        print("Compilation error: %s" % str(err))
        sys.exit(1)
    else:
        file = sys.stdout
        if a.output:
            file = open(a.output, "w")
        print(bf, file=file)


if __name__ == "__main__":
    _cli()
    
