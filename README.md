[![Downloads](https://static.pepy.tech/badge/bffuck)](https://pepy.tech/project/bffuck) [![Downloads](https://static.pepy.tech/badge/bffuck/month)](https://pepy.tech/project/bffuck) [![Downloads](https://static.pepy.tech/badge/bffuck/week)](https://pepy.tech/project/bffuck)

# BFFuck
 Makes brainfucking easier

The tools is an esoteric language that compiles to brainfuck, using algorithms in [brainfuck algorithms](https://esolangs.org/wiki/Brainfuck_algorithms).

### Usage:
Run this in Python:
```python
from bffuck import BFFuck
bff=BFFuck()
bf=bff.compile('Your code')
```

Note that if a BFFuck object is created and used, its status will change and therefore cannot compile another program.
### Syntax
BFFuck currently supports the following syntax:

Comment:
```
# Comment
```
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

Subtraction:
```
sub(x,<number>)
or
sub(x,<variable>)
```

Multiplication:
```
mul(x,<number>)
or
mul(x,<variable>)
```

Modulo:
```
mod(x,<number>)
or
mod(x,<variable>)
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

String output shortcut:
```text
print(STRING) # Without quotes
# For instance
print(Hello World!)
```

If statement:
```text
if(<variable or number>)
CODE
endif

if(<variable or number>)
CODE1
else
CODE2
endif
```

Comparison:
```text
lt(x,<number>) # Compares x and the variable or number, if x is less than the variable or number, set x to 1, otherwise 0
or
lt(x,<variable>)

eq(x,<number>) # Compares x and the variable or number, if x is equal to the variable or number, set x to 1, otherwise 0
or
eq(x,<variable>)
```

Macros:
```text
macro $<name> # Macro with no arguments
CODE
endmacro

macro $<name>(<arg1>,<arg2>,...) # Macro with arguments
CODE
endmacro

$<name> # Using a macro with no arguments
$<name>(<arg1>,<arg2>,...) # Using a macro with arguments
```

Memory:
```text
ptr(a,b) # Store address of a to variable b
```

### Platform
BFFuck is in **pure Python** and therefore it supports any platform.

### Constraints
Programs compiled from BFFuck needs you to have 8 bit cells that wrap.

### Disadvantages
BFFuck currently has these disadvantages:
1. <s>It's numbers are 8 bit numbers.</s> You can choose 8-bit, 16-bit or 32-bit numbers using the `byte` keyword argument. But you need to run it on a 8-bit interpreter. <font color="red">REMEMBER: Using numbers with more bits is slower and increases the size of program largely!</font>
2. It has some bugs.


The repository contains some examples, including a Hello World program, a cat program and an A+B program.
