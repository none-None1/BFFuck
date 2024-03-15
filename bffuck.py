import re

multipliers = ["[>++++++++++<-]>", "[<++++++++++>-]<"]
expanders = {
    1: {">": ">", "<": "<", "+": "+", "-": "-", "[": "[", "]": "]"},
    2: {
        ">": ">>>>",
        "<": "<<<<",
        "+": ">+<+[>-]>[->>+<]<<",
        "-": ">+<[>-]>[->>-<]<<-",
        "[": ">+<[>-]>[->+>[<-]<[<]>[-<+>]]<-[+<",
        "]": ">+<[>-]>[->+>[<-]<[<]>[-<+>]]<-]<",
    },
    4: {
        ">": ">>>>>",
        "<": "<<<<<",
        "+": "+[<+>>>>>+<<<<-]<[>+<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[->>+[<<+>>>>>+<<<-]<<[>>+<<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[->>>+[<<<+>>>>>+<<-]<<<[>>>+<<<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[->>>>+<<<<]]]>",
        "-": "[<+>>>>>+<<<<-]<[>+<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[->>[<<+>>>>>+<<<-]<<[>>+<<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[->>>[<<<+>>>>>+<<-]<<<[>>>+<<<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[->>>>-<<<<]>>>-<<<]>>-<<]>-",
        "[": "[>>>>+>>>>>+<<<<<<<<<-]>>>>>>>>>[<<<<<<<<<+>>>>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<<<[>>>+>>>>>+<<<<<<<<-]>>>>>>>>[<<<<<<<<+>>>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<<[>>+>>>>>+<<<<<<<-]>>>>>>>[<<<<<<<+>>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<[>+>>>>>+<<<<<<-]>>>>>>[<<<<<<+>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<<<<<[[-]>",
        "]": "[>>>>+>>>>>+<<<<<<<<<-]>>>>>>>>>[<<<<<<<<<+>>>>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<<<[>>>+>>>>>+<<<<<<<<-]>>>>>>>>[<<<<<<<<+>>>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<<[>>+>>>>>+<<<<<<<-]>>>>>>>[<<<<<<<+>>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<[>+>>>>>+<<<<<<-]>>>>>>[<<<<<<+>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<<<<<]>",
    },
}


def _power_series(k, m):
    x = int(k)
    if not k:
        return ""
    if not x and len(k) < 2:
        return ""
    if len(k) < 2:
        return "+" * x
    top, rest = k[0], k[1:]
    return "+" * int(top) + multipliers[m] + _power_series(rest, 1 - m)


def power_series(x):
    if not x:
        return ""
    if len(str(x)) & 1:
        return _power_series(str(x), 0)
    return _power_series(str(x), 0) + "[<+>-]<"


def getstr(x):
    normal, power = "+" * x, power_series(x)
    if len(normal) < len(power):
        return normal
    return power


class BFFuck(object):
    """Main implementation of BFFuck, a compiler making brainfucking easier"""

    def __init__(self, playfield=15):
        """Init object, playfield is the number of bytes used for temporary memory, the lesser the playfield is, the faster the final program is, but setting playfield to a number that is too small causes problems, especially if you want to use integer output."""
        self.valdict = {}  # Variable address
        self.bf = ""  # Brainfuck program
        self.ptr = 0  # Current pointer
        self.mem = playfield  # Leftmost unused memory
        self.stack = []  # Stack for while loop
        self.ifstack = []  # Stack for if statement
        self.ifvarstack = []
        self.whilevarstack = []
        self.haveelse = []
        self.playfield = playfield
        pass

    def movptr(self, pos):
        """Creates brainfuck that moves the pointer to a specific position"""
        if pos > self.ptr:
            p = ">" * (pos - self.ptr)
            self.ptr = pos
            return p
        if pos < self.ptr:
            p = "<" * (self.ptr - pos)
            self.ptr = pos
            return p
        return ""

    def program(self, code):
        """Compile one line of strict BFFuck program"""
        if "=" in code:
            v = code.split("=")
            if len(v) > 2:
                raise Exception("BFFuck currently does not support multiple ='s")
            val, stmt = v[0], v[1]
            if val in self.valdict:
                self.bf += self.movptr(self.valdict[val])
            else:
                self.bf += self.movptr(self.mem)
                self.valdict[val] = self.mem
                self.mem += 2
            if stmt == "inc":
                self.bf += ","
            elif stmt == "in":
                tmppos = self.ptr
                self.bf += self.movptr(0)
                self.bf += "[-]>[-]+[[-]>[-],[+[-----------[>[-]++++++[<------>-]<--<<[->>++++++++++<<]>>[-<<+>>]<+>]]]<]<"  # https://esolangs.org/wiki/Brainfuck_algorithms#Input_a_decimal_number
                self.bf += (
                    self.movptr(tmppos)
                    + "[-]"
                    + self.movptr(0)
                    + "["
                    + self.movptr(tmppos)
                    + "+"
                    + self.movptr(0)
                    + "-]"
                )
            elif stmt.isdigit():
                self.bf += "[-]"
                self.bf += "+" * int(stmt)
            else:
                if stmt in self.valdict:
                    self.bf += (
                        self.movptr(self.valdict[val])
                        + "[-]"
                        + self.movptr(self.valdict[stmt])
                    )
                    self.bf += (
                        "["
                        + self.movptr(self.valdict[val])
                        + "+"
                        + self.movptr(0)
                        + "+"
                        + self.movptr(self.valdict[stmt])
                        + "-"
                        + "]"
                        + self.movptr(0)
                        + "["
                        + self.movptr(self.valdict[stmt])
                        + "+"
                        + self.movptr(0)
                        + "-"
                        + "]"
                    )
                else:
                    raise Exception("Variable not found")
        else:
            if code.startswith("while("):
                if not (code.endswith(")")):
                    raise Exception("Unmatched bracket")
                else:
                    vn = code[6:-1]
                    if not vn.isdigit():
                        if vn not in self.valdict:
                            raise Exception("Variable not found")
                        else:
                            self.bf += self.movptr(self.valdict[vn])
                            self.bf += "["
                            self.stack.append(self.valdict[vn])
                    else:
                        if int(vn):  # while(1) is equivalent to while(2), while(3), etc
                            self.valdict["0"] = self.mem
                            self.mem += 2
                            self.bf += self.movptr(self.valdict["0"]) + "+["
                            self.stack.append(self.valdict["0"])
                        else:  # Skip program
                            self.temp = self.bf
                            self.stack.append(-1)
            elif code.startswith(
                "if("
            ):  # https://esolangs.org/wiki/Brainfuck_algorithms#if_(x)_{_code_}
                self.haveelse.append(False)
                if not (code.endswith(")")):
                    raise Exception("Unmatched bracket")
                else:
                    vn = code[3:-1]
                    x, y, z = self.mem, self.mem + 1, self.mem + 2
                    self.mem += 6
                    if not vn.isdigit():
                        if vn not in self.valdict:
                            raise Exception("Variable not found")
                        else:
                            self.bf += (
                                self.movptr(x)
                                + "["
                                + "-"
                                + "]"
                                + self.movptr(y)
                                + "["
                                + "-"
                                + "]"
                                + self.movptr(self.valdict[vn])
                                + "["
                                + self.movptr(x)
                                + "+"
                                + self.movptr(y)
                                + "+"
                                + self.movptr(self.valdict[vn])
                                + "-"
                                + "]"
                                + self.movptr(x)
                                + "["
                                + self.movptr(self.valdict[vn])
                                + "+"
                                + self.movptr(x)
                                + "-"
                                + "]+"
                                + self.movptr(y)
                                + "["
                            )
                            self.ifstack.append(self.valdict[vn])
                            self.ifvarstack.append(x)
                    else:
                        self.ifvarstack.append(-1)
                        if int(vn):
                            self.ifstack.append(-1)
                        else:
                            self.temp = self.bf
                            self.ifstack.append(-2)  # Skip program
            if code == "endif":
                if not self.ifstack:
                    raise Exception("End if without if")
                prev = self.ifstack.pop()
                x = self.ifvarstack.pop()
                if prev == -2:
                    self.bf = self.temp + "]"
                elif prev == -1:
                    pass
                else:
                    if not self.haveelse[-1]:
                        self.bf += self.movptr(x + 1) + "[-]]"
                    else:
                        self.bf += self.movptr(x) + "-]"
                    self.haveelse.pop()
            if code == "endwhile":
                if not self.stack:
                    raise Exception("End while without while")
                prev = self.stack.pop()
                if prev == -1:
                    self.bf = self.temp
                else:
                    self.bf += self.movptr(prev)
                    self.bf += "]"
            if code == "else":
                self.haveelse[-1] = True
                if not self.ifstack:
                    raise Exception("Else without if")
                prev = self.ifstack.pop()
                x = self.ifvarstack.pop()
                y = x + 1
                z = prev
                if prev == -2:
                    self.bf = self.temp + "]"
                    self.ifstack.append(-1)
                elif prev == -1:
                    self.temp = self.bf
                    self.ifstack.append(-2)
                else:
                    self.bf += (
                        self.movptr(x)
                        + "-"
                        + self.movptr(y)
                        + "[-]]"
                        + self.movptr(x)
                        + "["
                    )
                    self.ifstack.append(z)
                    self.ifvarstack.append(x)
            if code.startswith("outc("):
                if not (code.endswith(")")):
                    raise Exception("Unmatched bracket")
                else:
                    vn = code[5:-1]
                    if not vn.isdigit():
                        if vn not in self.valdict:
                            raise Exception("Variable not found")
                        else:
                            self.bf += self.movptr(self.valdict[vn])
                            self.bf += "."
                    else:
                        ivn = int(vn)
                        self.bf += self.movptr(0) + "[-]" + getstr(ivn) + ".[-]"
            elif code.startswith("out("):
                if not (code.endswith(")")):
                    raise Exception("Unmatched bracket")
                else:
                    vn = code[4:-1]
                    if not vn.isdigit():
                        if vn not in self.valdict:
                            raise Exception("Variable not found")
                        else:
                            self.bf += self.movptr(self.valdict[vn])
                            self.bf += (
                                "["
                                + self.movptr(0)
                                + "+"
                                + self.movptr(self.playfield - 1)
                                + "+"
                                + self.movptr(self.valdict[vn])
                                + "-]"
                            )
                            self.bf += (
                                self.movptr(0)
                                + ">[-]>[-]+>[-]+<[>[-<-<<[->+>+<<]>[-<+>]>>]++++++++++>[-]+>[-]>[-]>[-]<<<<<[->-[>+>>]>[[-<+>]+>+>>]<<<<<]>>-[-<<+>>]<[-]++++++++[-<++++++>]>>[-<<+>>]<<]<[.[-]<]<[-]"
                            )  # https://esolangs.org/wiki/Brainfuck_algorithms#Print_value_of_cell_x_as_number_for_ANY_sized_cell_(eg_8bit,_100000bit_etc)
                            self.bf += (
                                self.movptr(self.playfield - 1)
                                + "["
                                + self.movptr(self.valdict[vn])
                                + "+"
                                + self.movptr(self.playfield - 1)
                                + "-"
                                + "]"
                            )
                    else:
                        ivn = int(vn)
                        self.bf += (
                            self.movptr(0)
                            + "[-]"
                            + getstr(ivn)
                            + ">[-]>[-]+>[-]+<[>[-<-<<[->+>+<<]>[-<+>]>>]++++++++++>[-]+>[-]>[-]>[-]<<<<<[->-[>+>>]>[[-<+>]+>+>>]<<<<<]>>-[-<<+>>]<[-]++++++++[-<++++++>]>>[-<<+>>]<<]<[.[-]<]<[-]"
                        )
            elif code.startswith("add("):
                expr = code[4:-1]
                w = expr.split(",")
                if len(w) != 2:
                    raise Exception("add() needs 2 arguments")
                else:
                    a, b = w[0], w[1]
                    if a in self.valdict:
                        if b.isdigit():
                            self.bf += self.movptr(self.valdict[a])
                            self.bf += "+" * int(b)
                        else:
                            if b in self.valdict:
                                self.bf += (
                                    self.movptr(self.playfield - 1)
                                    + "[-]"
                                    + self.movptr(self.valdict[b])
                                    + "["
                                    + self.movptr(self.valdict[a])
                                    + "+"
                                    + self.movptr(self.playfield - 1)
                                    + "+"
                                    + self.movptr(self.valdict[b])
                                    + "-"
                                    + "]"
                                    + self.movptr(self.playfield - 1)
                                    + "["
                                    + self.movptr(self.valdict[b])
                                    + "+"
                                    + self.movptr(self.playfield - 1)
                                    + "-"
                                    + "]"
                                )  # https://esolangs.org/wiki/Brainfuck_algorithms#x%C2%B4_=_x_+_y
                            else:
                                raise Exception("Variable not found")
                    else:
                        raise Exception("Variable not found")
            elif code.startswith("sub("):
                expr = code[4:-1]
                w = expr.split(",")
                if len(w) != 2:
                    raise Exception("sub() needs 2 arguments")
                else:
                    a, b = w[0], w[1]
                    if a in self.valdict:
                        if b.isdigit():
                            self.bf += self.movptr(self.valdict[a])
                            self.bf += "-" * int(b)
                        else:
                            if b in self.valdict:
                                self.bf += (
                                    self.movptr(self.playfield - 1)
                                    + "[-]"
                                    + self.movptr(self.valdict[b])
                                    + "["
                                    + self.movptr(self.valdict[a])
                                    + "-"
                                    + self.movptr(self.playfield - 1)
                                    + "+"
                                    + self.movptr(self.valdict[b])
                                    + "-"
                                    + "]"
                                    + self.movptr(self.playfield - 1)
                                    + "["
                                    + self.movptr(self.valdict[b])
                                    + "+"
                                    + self.movptr(self.playfield - 1)
                                    + "-"
                                    + "]"
                                )  # https://esolangs.org/wiki/Brainfuck_algorithms#x%C2%B4_=_x_-_y
                            else:
                                raise Exception("Variable not found")
                    else:
                        raise Exception("Variable not found")
            elif code.startswith("mul("):
                expr = code[4:-1]
                w = expr.split(",")
                if len(w) != 2:
                    raise Exception("mul() needs 2 arguments")
                else:
                    a, b = w[0], w[1]
                    tmppos = self.ptr
                    if a in self.valdict:
                        if b.isdigit():
                            self.bf += (
                                self.movptr(self.playfield - 3)
                                + "[-]"
                                + "+" * int(b)
                                + self.movptr(self.playfield - 1)
                                + "["
                                + "-"
                                + "]"
                                + self.movptr(self.playfield - 2)
                                + "["
                                + "-"
                                + "]"
                                + self.movptr(self.valdict[a])
                                + "["
                                + self.movptr(self.playfield - 2)
                                + "+"
                                + self.movptr(self.valdict[a])
                                + "-"
                                + "]"
                                + self.movptr(self.playfield - 2)
                                + "["
                                + self.movptr(self.playfield - 3)
                                + "["
                                + self.movptr(self.valdict[a])
                                + "+"
                                + self.movptr(self.playfield - 1)
                                + "+"
                                + self.movptr(self.playfield - 3)
                                + "-"
                                + "]"
                                + self.movptr(self.playfield - 1)
                                + "["
                                + self.movptr(self.playfield - 3)
                                + "+"
                                + self.movptr(self.playfield - 1)
                                + "-"
                                + "]"
                                + self.movptr(self.playfield - 2)
                                + "-"
                                + "]"
                                + self.movptr(self.playfield - 3)
                                + "[-]"
                            )
                        else:
                            if b in self.valdict:
                                self.bf += (
                                    self.movptr(self.playfield - 1)
                                    + "["
                                    + "-"
                                    + "]"
                                    + self.movptr(self.playfield - 2)
                                    + "["
                                    + "-"
                                    + "]"
                                    + self.movptr(self.valdict[a])
                                    + "["
                                    + self.movptr(self.playfield - 2)
                                    + "+"
                                    + self.movptr(self.valdict[a])
                                    + "-"
                                    + "]"
                                    + self.movptr(self.playfield - 2)
                                    + "["
                                    + self.movptr(self.valdict[b])
                                    + "["
                                    + self.movptr(self.valdict[a])
                                    + "+"
                                    + self.movptr(self.playfield - 1)
                                    + "+"
                                    + self.movptr(self.valdict[b])
                                    + "-"
                                    + "]"
                                    + self.movptr(self.playfield - 1)
                                    + "["
                                    + self.movptr(self.valdict[b])
                                    + "+"
                                    + self.movptr(self.playfield - 1)
                                    + "-"
                                    + "]"
                                    + self.movptr(self.playfield - 2)
                                    + "-"
                                    + "]"
                                )
                            else:
                                raise Exception("Variable not found")
                    else:
                        raise Exception("Variable not found")
            elif code.startswith("lt("):
                expr = code[3:-1]
                w = expr.split(",")
                if len(w) != 2:
                    raise Exception("lt() needs 2 arguments")
                else:
                    a, b = w[0], w[1]
                    tmppos = self.ptr
                    if a in self.valdict:
                        post = False
                        if b.isdigit():
                            self.bf += self.movptr(self.playfield - 1) + "+" * int(b)
                            b = self.playfield - 1
                            post = True
                        else:
                            if b in self.valdict:
                                b = self.valdict[b]
                            else:
                                raise Exception("Variable not found")
                        self.bf += (
                            self.movptr(0)
                            + "["
                            + "-"
                            + "]"
                            + self.movptr(1)
                            + "["
                            + "-"
                            + "]"
                            + ">"
                            + "["
                            + "-"
                            + "]"
                            + "+"
                            + ">"
                            + "["
                            + "-"
                            + "]"
                            + "<"
                            + "<"
                            + self.movptr(b)
                            + "["
                            + self.movptr(0)
                            + "+"
                            + self.movptr(1)
                            + "+"
                            + self.movptr(b)
                            + "-"
                            + "]"
                            + self.movptr(0)
                            + "["
                            + self.movptr(b)
                            + "+"
                            + self.movptr(0)
                            + "-"
                            + "]"
                            + self.movptr(self.valdict[a])
                            + "["
                            + self.movptr(0)
                            + "+"
                            + self.movptr(self.valdict[a])
                            + "-"
                            + "]"
                            + "+"
                            + self.movptr(1)
                            + "["
                            + ">"
                            + "-"
                            + "]"
                            + ">"
                            + "["
                            + "<"
                            + self.movptr(self.valdict[a])
                            + "-"
                            + self.movptr(0)
                            + "["
                            + "-"
                            + "]"
                            + self.movptr(1)
                            + ">"
                            + "-"
                            + ">"
                            + "]"
                            + "<"
                            + "+"
                            + "<"
                            + self.movptr(0)
                            + "["
                            + self.movptr(1)
                            + "-"
                            + "["
                            + ">"
                            + "-"
                            + "]"
                            + ">"
                            + "["
                            + "<"
                            + self.movptr(self.valdict[a])
                            + "-"
                            + self.movptr(0)
                            + "["
                            + "-"
                            + "]"
                            + "+"
                            + self.movptr(1)
                            + ">"
                            + "-"
                            + ">"
                            + "]"
                            + "<"
                            + "+"
                            + "<"
                            + self.movptr(0)
                            + "-"
                            + "]"
                        )  # https://esolangs.org/wiki/Brainfuck_algorithms#x%C2%B4_=_x_%3C_y
                        if post:
                            self.bf += self.movptr(b) + "[-]"
                    else:
                        raise Exception("Variable not found")
            elif code.startswith("eq("):
                expr = code[3:-1]
                w = expr.split(",")
                if len(w) != 2:
                    raise Exception("eq() needs 2 arguments")
                else:
                    a, b = w[0], w[1]
                    tmppos = self.ptr
                    if a in self.valdict:
                        post = False
                        if b.isdigit():
                            self.bf += self.movptr(self.playfield - 3) + "+" * int(b)
                            b = self.playfield - 3
                            post = True
                        else:
                            if b in self.valdict:
                                b = self.valdict[b]
                            else:
                                raise Exception("Variable not found")
                        self.bf += (
                            self.movptr(self.playfield - 1)
                            + "["
                            + "-"
                            + "]"
                            + self.movptr(self.playfield - 2)
                            + "["
                            + "-"
                            + "]"
                            + self.movptr(self.valdict[a])
                            + "["
                            + self.movptr(self.playfield - 2)
                            + "+"
                            + self.movptr(self.valdict[a])
                            + "-"
                            + "]"
                            + "+"
                            + self.movptr(b)
                            + "["
                            + self.movptr(self.playfield - 2)
                            + "-"
                            + self.movptr(self.playfield - 1)
                            + "+"
                            + self.movptr(b)
                            + "-"
                            + "]"
                            + self.movptr(self.playfield - 1)
                            + "["
                            + self.movptr(b)
                            + "+"
                            + self.movptr(self.playfield - 1)
                            + "-"
                            + "]"
                            + self.movptr(self.playfield - 2)
                            + "["
                            + self.movptr(self.valdict[a])
                            + "-"
                            + self.movptr(self.playfield - 2)
                            + "["
                            + "-"
                            + "]"
                            + "]"
                        )  # https://esolangs.org/wiki/Brainfuck_algorithms#x%C2%B4_=_x_==_y
                        if post:
                            self.bf += self.movptr(b) + "[-]"
                    else:
                        raise Exception("Variable not found")
            elif code.startswith("mod("):
                expr = code[4:-1]
                w = expr.split(",")
                if len(w) != 2:
                    raise Exception("mod() needs 2 arguments")
                else:
                    a, b = w[0], w[1]
                    if a in self.valdict:
                        self.bf += (
                            self.movptr(self.valdict[a])
                            + "["
                            + self.movptr(1)
                            + "+"
                            + self.movptr(self.valdict[a])
                            + "-]"
                        )
                        if b.isdigit():
                            self.bf += self.movptr(3) + "+" * int(b)
                            post = False
                        else:
                            if b in self.valdict:
                                self.bf += (
                                    self.movptr(self.valdict[b])
                                    + "["
                                    + self.movptr(3)
                                    + "+"
                                    + self.movptr(self.playfield - 1)
                                    + "+"
                                    + self.movptr(self.valdict[b])
                                    + "-]"
                                )
                                post = True
                            else:
                                raise Exception("Variable not found")
                        self.bf += (
                            self.movptr(1)
                            + "[>+>->+<[>]>[<+>-]<<[<]>-]"
                            + self.movptr(2)
                            + "[-]"
                            + self.movptr(3)
                            + "[-]"
                            + self.movptr(4)
                            + "["
                            + self.movptr(self.valdict[a])
                            + "+"
                            + self.movptr(4)
                            + "-]"
                        )  # https://esolangs.org/wiki/Brainfuck_algorithms#Modulus_algorithm
                        if post:
                            self.bf += (
                                self.movptr(self.playfield - 1)
                                + "["
                                + self.movptr(self.valdict[b])
                                + "+"
                                + self.movptr(self.playfield - 1)
                                + "-]"
                            )
                    else:
                        raise Exception("Variable not found")
            elif code.startswith("print("):
                if not (code.endswith(")")):
                    raise Exception("Unmatched bracket")
                s = code[6:-1]
                tmppos = self.ptr
                self.bf += self.movptr(self.playfield - 2)
                for i in s:
                    if ord(i) > 255:
                        raise Exception("print() only supports ASCII")
                    else:
                        self.bf += getstr(ord(i)) + "." + "[-]"
                self.bf += self.movptr(tmppos)
            elif code.startswith("ptr("):
                if not (code.endswith(")")):
                    raise Exception("Unmatched bracket")
                a, b = code[4:-1].split(",")
                if a not in self.valdict or b not in self.valdict:
                    raise Exception("Variable not found")
                self.bf += self.movptr(self.valdict[b]) + getstr(self.valdict[a])
            elif code.startswith("bf "):
                self.bf += code[4:-1]
            elif code.startswith("ref("):
                if not (code.endswith(")")):
                    raise Exception("Unmatched bracket")
                a, b = code[4:-1].split(",")
                if a not in self.valdict:
                    raise Exception("Variable not found")
                if b.isdigit():
                    b = int(b)
                    self.bf += (
                        self.movptr(0)
                        + "[-]"
                        + self.movptr(b)
                        + "["
                        + self.movptr(0)
                        + "+"
                        + self.movptr(1)
                        + "+"
                        + self.movptr(b)
                        + "-]"
                        + self.movptr(self.valdict[a])
                        + "[-]"
                        + self.movptr(0)
                        + "["
                        + self.movptr(self.valdict[a])
                        + "+"
                        + self.movptr(0)
                        + "-"
                        + "]"
                        + self.movptr(1)
                        + "["
                        + self.movptr(b)
                        + "+"
                        + self.movptr(1)
                        + "-]"
                    )
                else:
                    if b not in self.valdict:
                        raise Exception("Variable not found")
                    else:
                        self.bf += (
                            self.movptr(self.valdict[a])
                            + "[-]"
                            + self.movptr(self.playfield - 4)
                            + "[-]"
                            + self.movptr(self.valdict[b])
                            + "["
                            + self.movptr(self.playfield - 2)
                            + "+"
                            + self.movptr(self.playfield - 8)
                            + "+"
                            + self.movptr(self.valdict[b])
                            + "-]"
                            + self.movptr(self.playfield - 5)
                            + "[-]++"
                            + self.movptr(self.playfield - 1)
                            + "[-]+"
                            + self.movptr(self.playfield - 2)
                            + "-" * (self.playfield - 2)
                            + "["
                            + self.movptr(self.playfield - 1)
                            + "-[+>>-]>>[-]+<<--[++<<--]++>>>>"
                            + self.movptr(self.playfield - 2)
                            + "--]"
                            + self.movptr(self.playfield - 1)
                            + "-[+>>-]+<[>--[++<<--]++<+>>>>>-[+>>-]+<-]>--[++<<--]++>>>>"
                            + self.movptr(self.playfield - 8)
                            + "["
                            + self.movptr(self.valdict[b])
                            + "+"
                            + self.movptr(self.playfield - 8)
                            + "-]"
                            + self.movptr(self.playfield - 6)
                            + "["
                            + self.movptr(self.valdict[a])
                            + "+"
                            + self.movptr(self.playfield - 1)
                            + "-[+>>-]+<+>--[++<<--]++>>>>"
                            + self.movptr(self.playfield - 6)
                            + "-]"
                        )
            elif code.startswith("set("):
                if not (code.endswith(")")):
                    raise Exception("Unmatched bracket")
                a, b = code[4:-1].split(",")
                if not a.isdigit():
                    if a not in self.valdict:
                        raise Exception("Variable not found")
                    else:
                        self.bf += (
                            self.movptr(self.playfield - 11)
                            + "[-]"
                            + self.movptr(self.playfield - 10)
                            + "[-]"
                            + self.movptr(self.valdict[a])
                            + "["
                            + self.movptr(self.playfield - 11)
                            + "+"
                            + self.movptr(self.playfield - 10)
                            + "+"
                            + self.movptr(self.valdict[a])
                            + "-]"
                            + self.movptr(self.playfield - 11)
                            + "["
                            + self.movptr(self.valdict[a])
                            + "+"
                            + self.movptr(self.playfield - 11)
                            + "-]"
                        )
                else:
                    self.bf += self.movptr(self.playfield - 10) + "[-]" + getstr(int(a))
                if b.isdigit():
                    b = int(b)
                    self.bf += (
                        self.movptr(b)
                        + "[-]"
                        + self.movptr(self.playfield - 10)
                        + "["
                        + self.movptr(b)
                        + "+"
                        + self.movptr(self.playfield - 10)
                        + "-]"
                    )
                else:
                    if b not in self.valdict:
                        raise Exception("Variable not found")
                    else:
                        self.bf += (
                            self.movptr(self.playfield - 4)
                            + "[-]"
                            + self.movptr(self.valdict[b])
                            + "["
                            + self.movptr(self.playfield - 2)
                            + "+"
                            + self.movptr(self.playfield - 8)
                            + "+"
                            + self.movptr(self.valdict[b])
                            + "-]"
                            + self.movptr(self.playfield - 5)
                            + "[-]++"
                            + self.movptr(self.playfield - 1)
                            + "[-]+"
                            + self.movptr(self.playfield - 2)
                            + "-" * (self.playfield - 2)
                            + "["
                            + self.movptr(self.playfield - 1)
                            + "-[+>>-]>>[-]+<<--[++<<--]++>>>>"
                            + self.movptr(self.playfield - 2)
                            + "--]"
                            + self.movptr(self.playfield - 1)
                            + "-[+>>-]+<[-]>--[++<<--]++<<<<<[>>>>>>>>>-[+>>-]+<+>--[++<<--]++<<<<<-]>>>>>>>>>"
                            + self.movptr(self.playfield - 8)
                            + "["
                            + self.movptr(self.valdict[b])
                            + "+"
                            + self.movptr(self.playfield - 8)
                            + "-]"
                        )

    def join_semantically(self, strings):
        res = strings[0]
        for i, j in enumerate(strings):
            if i == len(strings) - 1:
                break
            if j[-1].isalpha() and strings[i + 1][0].isalpha():
                res += " " + strings[i + 1]
            else:
                res += strings[i + 1]
        return res

    def opt(self, prog):
        """Finally optimization!"""
        curch = ""
        curnum = 0
        temp = []
        prog += "@"
        for i in prog:
            if i == curch:
                curnum += 1
            else:
                curnum += 1
                temp.append((curnum, curch))
                curch = i
                curnum = 0
        temp.append(("_", 0))
        out = ""
        dct = {"+": "-", ">": "<", "-": "+", "<": ">"}
        curch = ""
        curnum = 0
        for i, j in temp:
            if j in dct:
                if curch in dct and j == dct[curch]:
                    curnum -= i
                    if curnum < 0:
                        curch = dct[curch]
                        curnum = -curnum
                else:
                    out += curch * curnum
                    if curch != j:
                        curnum = 0
                    curnum = i
                    curch = j
            else:
                if curch:
                    out += curch * curnum
                curch = ""
                out += j * i
        return out.rstrip("+-><")

    def expand(self, prog, byte):
        """Expand program"""
        if byte not in (1, 2, 4):
            raise ValueError("Byte should by 1, 2, or 4, not {}".format(byte))
        res = "" if byte != 4 else ">"
        for i in prog:
            if i in expanders[byte]:
                res += expanders[byte][i]
            else:
                res += i
        return res

    def getmacros(self, prog):
        macros = {}
        macro = []
        no_macro = []
        macro_name = ""
        for i in prog.split("\n"):
            i = i.strip()
            if i == "endmacro":
                macros[macro_name] = macro
                macro_name = ""
                macro = []
                continue
            if macro_name:
                macro.append(i)
                continue
            y = i
            while "  " in y:
                y = y.replace("  ", " ")
            y, k = y[: y.find(" ")], y[y.find(" ") :].replace(" ", "")
            if y == "macro":
                if not k.startswith("$"):
                    raise SyntaxError("Macros must start with '$'")
                macro_name = k
            else:
                no_macro.append(i)
        return (macros, "\n".join(no_macro))

    def can_be_preprocessed(self, prog):
        macros, no_macro = self.getmacros(prog)
        for i in no_macro.split("\n"):
            if i.startswith("$"):
                return True
        return False

    def preprocess(self, macros, no_macro):
        """Preprocess macros"""
        res = []
        for i in no_macro.split("\n"):
            i = i.split("#")[0].strip()
            if i.startswith("$"):
                if "(" not in i:
                    res += macros[i]
                else:
                    mac_name, mac_args = i[: i.find("(")], i[i.find("(") :]
                    for name, info in macros.items():
                        if name.startswith(mac_name + "("):
                            _args = name[name.find("(") :]
                            args1, args2 = mac_args[1:-1].split(","), _args[1:-1].split(
                                ","
                            )
                            if len(args1) != len(args2):
                                raise SyntaxError("Argument table length wrong")
                            for j in info:
                                if j.strip().startswith("print("):
                                    res.append(j)
                                else:
                                    t = j
                                    for _i, _j in zip(args2, args1):
                                        t = re.sub("\\b" + re.escape(_i) + "\\b", _j, t)
                                    res.append(t)
                            break

            else:
                res.append(i)
        return "\n".join(res)

    def compile(self, prog, byte=1):
        """Compiles BFFuck programs into brainfuck"""
        clean = ""
        macros, no_macro = self.getmacros(prog)
        while self.can_be_preprocessed(prog):
            prog = self.preprocess(macros, no_macro)
            _, no_macro = self.getmacros(prog)
        for i in prog.split("\n"):
            if len(i.strip()) == 0:
                continue
            if i.strip().startswith("print(") or i.strip().startswith("bf "):
                clean = i.strip()  # Print and bf need to preserve whitespaces
            else:
                clean = self.join_semantically(i.split()).split("#")[0]
            self.program(clean)
        return self.opt(self.expand(self.opt(self.bf), byte))
