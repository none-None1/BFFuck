# BFFuck
 Makes brainfucking easier

This is a work in progress

The tools is an esoteric language that compiles to brainfuck, using algorithms in [brainfuck algorithms](https://esolangs.org/wiki/Brainfuck_algorithms).

### Usage:
Run this in Python:
```python
from bffuck import BFFuck
bff=BFFuck()
bf=bff.compile('Your code')
```

### Syntax
BFFuck currently supports the following syntax:

Variable definition:
```text
<variable 1>=<variable 2>
or
<variable>=<number>
```

Addition:
```text
add(x,<number>)
or
add(x,<variable>)
```

While loop:
```text
while(<variable or number>)
CODE
endwhile
```

I/O:
```text
<variable>=in # Reads <variable> as decimal integer
<variable>=inc # Reads <variable> as ASCII character
out(<variable or number>) # Outputs <variable> as decimal integer
outc(<variable or number>) # Outputs <variable> as ASCII character
```

### Platform
BFFuck is in **pure Python** and therefore it supports any platform.

### Constraints
Programs compiled from BFFuck needs you to have 8 bit cells that wrap.

### Disadvantages
BFFuck currently has these disadvantages:
1. It's numbers are 8 bit numbers.
2. The program it generates is unoptimized.
3. The program has some of bugs (e.g. You can use "end while" instead of "endwhile", but that shouldn't be allowed).

The repository contains some examples, including a cat program and an A+B program.
