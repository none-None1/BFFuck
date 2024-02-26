multipliers=['[>++++++++++<-]>','[<++++++++++>-]<']
expanders={1: {'>': '>', '<': '<', '+': '+', '-': '-', '[': '[', ']': ']'}, 2: {'>': '>>>>', '<': '<<<<', '+': '>+<+[>-]>[->>+<]<<', '-': '>+<[>-]>[->>-<]<<-', '[': '>+<[>-]>[->+>[<-]<[<]>[-<+>]]<-[+<', ']': '>+<[>-]>[->+>[<-]<[<]>[-<+>]]<-]<'}, 4: {'>': '>>>>>', '<': '<<<<<', '+': '+[<+>>>>>+<<<<-]<[>+<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[->>+[<<+>>>>>+<<<-]<<[>>+<<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[->>>+[<<<+>>>>>+<<-]<<<[>>>+<<<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[->>>>+<<<<]]]>', '-': '[<+>>>>>+<<<<-]<[>+<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[->>[<<+>>>>>+<<<-]<<[>>+<<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[->>>[<<<+>>>>>+<<-]<<<[>>>+<<<-]+>>>>>[<<<<<->>>>>[-]]<<<<<[->>>>-<<<<]>>>-<<<]>>-<<]>-', '[': '[>>>>+>>>>>+<<<<<<<<<-]>>>>>>>>>[<<<<<<<<<+>>>>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<<<[>>>+>>>>>+<<<<<<<<-]>>>>>>>>[<<<<<<<<+>>>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<<[>>+>>>>>+<<<<<<<-]>>>>>>>[<<<<<<<+>>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<[>+>>>>>+<<<<<<-]>>>>>>[<<<<<<+>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<<<<<[[-]>', ']': '[>>>>+>>>>>+<<<<<<<<<-]>>>>>>>>>[<<<<<<<<<+>>>>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<<<[>>>+>>>>>+<<<<<<<<-]>>>>>>>>[<<<<<<<<+>>>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<<[>>+>>>>>+<<<<<<<-]>>>>>>>[<<<<<<<+>>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<[>+>>>>>+<<<<<<-]>>>>>>[<<<<<<+>>>>>>-]<<<<<[[-]<<<<<+>>>>>]<<<<<]>'}}
def _power_series(x,m):
    if not x:
        return ''
    if x<10:
        return '+'*x
    x=str(x)
    top,rest=x[0],x[1:]
    return '+'*int(top)+multipliers[m]+_power_series(int(rest),1-m)
def power_series(x):
    if not x:
        return ''
    if len(str(x))&1:
        return _power_series(x,0)
    return _power_series(x,0)+'[<+>-]'
def getstr(x):
    normal,power='+'*x,power_series(x)
    if len(normal)<len(power):
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
        self.haveelse=[]
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
                self.mem += 1
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
                            self.mem += 1
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
                    x,y,z=self.mem,self.mem+1,self.mem+2
                    self.mem+=3
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
                x=self.ifvarstack.pop()
                if prev == -2:
                    self.bf = self.temp + "]"
                elif prev == -1:
                    pass
                else:
                    if not self.haveelse[-1]:
                        self.bf += self.movptr(x+1) + "[-]]"
                    else:
                        self.bf+=self.movptr(x)+'-]'
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
                self.haveelse[-1]=True
                if not self.ifstack:
                    raise Exception("Else without if")
                prev = self.ifstack.pop()
                x=self.ifvarstack.pop()
                y=x+1
                z=prev
                if prev == -2:
                    self.bf = self.temp + "]"
                    self.ifstack.append(-1)
                elif prev == -1:
                    self.temp = self.bf
                    self.ifstack.append(-2)
                else:
                    self.bf+=self.movptr(x)+'-'+self.movptr(y)+"[-]]"+self.movptr(x)+"["
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
                        self.bf += (
                            self.movptr(0)
                            + "[-]"
                            + getstr(ivn)
                            + ".[-]"
                        )
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
                self.bf += self.movptr(self.playfield - 1)
                for i in s:
                    if ord(i) > 255:
                        raise Exception("print() only supports ASCII")
                    else:
                        self.bf += (
                            ("+" * ord(i) if ord(i) < 128 else "-" * ord(256 - i))
                            + "."
                            + "[-]"
                        )
                self.bf += self.movptr(tmppos)

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
        if byte not in (1,2,4):
            raise ValueError('Byte should by 1, 2, or 4, not {}'.format(byte))
        res=('' if byte!=4 else '>')
        for i in prog:
            if i in expanders[byte]:
                res+=expanders[byte][i]
            else:
                res+=i
        return res
    def compile(self, prog, byte=1):
        """Compiles BFFuck programs into brainfuck"""
        clean = ""
        for i in prog.split("\n"):
            if len(i.strip()) == 0:
                continue
            if i.strip().startswith("print("):
                clean = i.strip()  # Print needs to preserve whitespaces
            else:
                clean = self.join_semantically(i.split()).split("#")[0]
            self.program(clean)
        return self.opt(self.expand(self.opt(self.bf),byte))
