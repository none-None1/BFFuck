class BFFuck(object):
    """Main implemntation of BFFuck, a compiler making brainfucking easier"""
    def __init__(self,playfield=10):
        """Init object, playfield is the number of bytes used for temporary memory, the lesser the playfield is, the faster the final program is, but setting playfield to a number that is too small causes problems, especially if you want to use integer output."""
        self.valdict={} # Variable address
        self.bf='' # Brainfuck program
        self.ptr=0 # Current pointer
        self.mem=playfield # Leftmost unused memory
        self.stack=[]
        pass
    def movptr(self,pos):
        """Creates brainfuck that moves the pointer to a specific position"""
        if pos>self.ptr:
            p='>'*(pos-self.ptr)
            self.ptr=pos
            return p
        if pos<self.ptr:
            p='<' * (self.ptr-pos)
            self.ptr = pos
            return p
        return ''
    def program(self,code):
        """Compile one line of strict BFFuck program"""
        if '=' in code:
            v=code.split('=')
            if len(v)>2:
                raise Exception('BFFuck currently does not support multiple =\'s')
            val,stmt=v[0],v[1]
            if val in self.valdict:
                self.bf+=self.movptr(self.valdict[val])
            else:
                self.bf += self.movptr(self.mem)
                self.valdict[val]=self.mem
                self.mem+=1
            if stmt=='inc':
                self.bf+=','
            elif stmt=='in':
                tmppos=self.ptr
                self.bf+=self.movptr(0)
                self.bf+='[-]>[-]+[[-]>[-],[+[-----------[>[-]++++++[<------>-]<--<<[->>++++++++++<<]>>[-<<+>>]<+>]]]<]<' # https://esolangs.org/wiki/Brainfuck_algorithms#Input_a_decimal_number
                self.bf+=self.movptr(tmppos)+'[-]'+self.movptr(0)+'['+self.movptr(tmppos)+'+'+self.movptr(0)+'-]'
            elif stmt.isdigit():
                self.bf+='[-]'
                self.bf+='+'*int(stmt)
            else:
                if stmt in self.valdict:
                    self.bf += self.movptr(self.valdict[val])+'[-]'+self.movptr(self.valdict[stmt])
                    self.bf+='['+self.movptr(self.valdict[val])+'+'+self.movptr(0)+'+'+self.movptr(self.valdict[stmt])+'-'+']'+self.movptr(0)+'['+self.movptr(self.valdict[stmt])+'+'+self.movptr(0)+'-'+']'
                else:
                    raise Exception('Variable not found')
        else:
            if code.startswith('while('):
                if not (code.endswith(')')):
                    raise Exception('Unmatched bracket')
                else:
                    vn = code[6:-1]
                    if not vn.isdigit():
                        if vn not in self.valdict:
                            raise Exception('Variable not found')
                        else:
                            self.bf += self.movptr(self.valdict[vn])
                            self.bf += '['
                            self.stack.append(self.valdict[vn])
                    else:
                        if int(vn): # while(1) is equivalent to while(2), while(3), etc
                            self.valdict['0'] = self.mem
                            self.mem += 1
                            self.bf += self.movptr(self.valdict['0']) + '+['
                            self.stack.append(self.valdict['0'])
                        else: # Skip program
                            self.temp=self.bf
                            self.stack.append(-1)
            if code=='endwhile':
                if not self.stack:
                    raise Exception('End while without while')
                prev=self.stack.pop()
                if prev==-1:
                    self.bf=self.temp
                else:
                    self.bf+=self.movptr(prev)
                    self.bf+=']'

            if code.startswith('outc('):
                if not (code.endswith(')')):
                    raise Exception('Unmatched bracket')
                else:
                    vn=code[5:-1]
                    if not vn.isdigit():
                        if vn not in self.valdict:
                            raise Exception('Variable not found')
                        else:
                            self.bf+=self.movptr(self.valdict[vn])
                            self.bf+='.'
                    else:
                        self.bf+=self.movptr(0)+'+'*int(vn)+'.[-]'
            elif code.startswith('out('):
                if not (code.endswith(')')):
                    raise Exception('Unmatched bracket')
                else:
                    vn = code[4:-1]
                    if not vn.isdigit():
                        if vn not in self.valdict:
                            raise Exception('Variable not found')
                        else:
                            self.bf += self.movptr(self.valdict[vn])
                            self.bf += '['+self.movptr(0)+'+'+self.movptr(1)+'+'+self.movptr(self.valdict[vn])+'-]'
                            self.bf+=self.movptr(0)+'>>++++++++++<<[->+>-[>+>>]>[+[-<+>]>+>>]<<<<<<]>>[-]>>>++++++++++<[->-[>+>>]>[+[-<+>]>+>>]<<<<<]>[-]>>[>++++++[-<++++++++>]<.<<+>+>[-]]<[<[->-<]++++++[->++++++++<]>.[-]]<<++++++[-<++++++++>]<.[-]<<[-<+>]<[-]' # https://esolangs.org/wiki/Brainfuck_algorithms#Print_value_of_cell_x_as_number_(8-bit)
                            self.bf+= self.movptr(1)+'['+self.movptr(self.valdict[vn])+'+'+self.movptr(1)+'-'+']'
                    else:
                        self.bf += self.movptr(0) + '+' * int(vn) +  '>>++++++++++<<[->+>-[>+>>]>[+[-<+>]>+>>]<<<<<<]>>[-]>>>++++++++++<[->-[>+>>]>[+[-<+>]>+>>]<<<<<]>[-]>>[>++++++[-<++++++++>]<.<<+>+>[-]]<[<[->-<]++++++[->++++++++<]>.[-]]<<++++++[-<++++++++>]<.[-]<<[-<+>]<[-]'
            elif code.startswith('add('):
                expr = code[4:-1]
                w=expr.split(',')
                if(len(w)!=2):
                    raise Exception('add() needs 2 arguments')
                else:
                    a,b=w[0],w[1]
                    if a in self.valdict:
                        if b.isdigit():
                            self.bf+=self.movptr(self.valdict[a])
                            self.bf+='+'*int(b)
                        else:
                            if b in self.valdict:
                                self.bf+=self.movptr(self.valdict[b])+'['+self.movptr(self.valdict[a])+'+'+self.movptr(0)+'+'+self.movptr(self.valdict[b])+'-'+']'+self.movptr(0)+'['+self.movptr(self.valdict[b])+'+'+self.movptr(0)+'-'+']'
                            else:
                                raise Exception('Variable not found')
                    else:
                        raise Exception('Variable not found')
    def compile(self,prog):
        """Compiles BFFuck programs into brainfuck"""
        clean=''
        for i in prog.split('\n'):
            clean=''.join(i.split()).split('#')[0]
            self.program(clean)
        return self.bf
