# BFFuck
 Makes brainfucking easier

This is a work in progress

### Usage:
Run this in Python:
```python
from bffuck import BFFuck
bff=BFFuck()
bf=bff.compile('Your code')
```

### Syntax
BFFuck supports the following syntax:
Variable definition:
```
<variable 1>=<variable 2>
or
<variable>=<number>
```

Addition:
```
add(x,<number>)
or
add(x,<variable>)
```

While loop:
```
while(<variable or number>)
CODE
endwhile
```

I/O:
```
<variable>=in # Reads <variable> as decimal integer
<variable>=inc # Reads <variable> as ASCII character
out(<variable or number>) # Outputs <variable> as decimal integer
outc(<variable or number>) # Outputs <variable> as ASCII character
```
### Disadvantages
BFFuck currently has these disadvantages:
1. It's numbers are 8 bit numbers.
2. The program it generates is unoptimized.
3. The program has a lot of bugs (e.g. You can use "end while" instead of "endwhile", but that shouldn't be allowed).
