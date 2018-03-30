#!-
import sys, re
import ipdb
import os
EOF = b'\x00'

INVALID_TOKEN = 0
RELOP = "Relop"
RESERVED = "Reserved"
SYMBOL = "Symbol"
NUMBER = "Numeric"
OPERATOR = "Operator"

GT = 1;LT = 2;EQ = 3;LE = 4;GE = 5; NE = 6;
NUM = 7;ID = 8
IF  = 9; ELSE = 10; FOR = 11; WHILE = 12;DO = 13; 
OPRQ = 14; CLRQ = 15; OPFQ = 16; CLFQ = 17; OPSQ = 18;CLSQ = 19
PRINT = 20
ENDSTMT = 21;
INT=22;STRING=23;CHAR=24;VOID=25; UINT = 26;FLOAT=31;
SET=27;PLUS=28;MINUS=29;MULT=30; PLSET = 32; MUSET = 33; MISET = 34;DIV=35;DISET=36;MOD=37;MOSET=38
DOT=39;ZP = 40;
SHR = 41; SHL = 42;
INCLUDE = 43; DEFINE = 44;

KEYWORDS = {IF: re.compile(r'^(if)[ (]'), 
            ELSE:re.compile(r'^(else)[ (]'), 
            FOR: re.compile(r'^(for)[ (]'), 
            WHILE: re.compile(r'^(while)[ (]'), 
            DO: re.compile(r'^(do)[ {]'), 
            PRINT: re.compile(r'^(print)[ (]'),
            INT: re.compile(r'^(int)[ ()\*]'),
            CHAR: re.compile(r'^(char)[ ()\*]'),
            VOID: re.compile(r'^(void)[ ()\*]'),
            STRING: re.compile(r'^(string)[ ()\*]'),
            FLOAT: re.compile(r'^(float)[ ()\*]'),
            UINT: re.compile(r'^(uint)[ ()\*]'),
            INCLUDE: re.compile(r'^(#include)[ <]'),
            DEFINE: re.compile(r'^(#define)[ <]')
            }
ID_RE = re.compile(r'^([a-zA-Z]+[_0-9A-Za-z]*)[^_0-9A-Za-z]')
NUM_RE = re.compile(r'^([0-9]+)(\.[0-9]*)?([Ee][+-][0-9]*)?[^0-9]')

DEL_RE = re.compile(r"[ \t]")


class Token:
        name = ''
        attribute = INVALID_TOKEN
        
        def __init__(self, name='', attribute=INVALID_TOKEN):
                self.name = name
                self.attribute = attribute

class Lexer():
        def __init__(self, input_text):
                self.input = input_text + ' ' + EOF
                self.position = 0
                self.forward = 0
                self.lexeme_begin = 0
                self.tokens = []
                self.lines = 0

        def GetNextToken(self):
                if self.input[self.lexeme_begin] != EOF:
                      
                        print("Parsing %s" % self.input[self.lexeme_begin: self.lexeme_begin + 15])
                        c = self.input[self.lexeme_begin]
                        while (DEL_RE.match(c) is not None) or (c== '\n'):
                                if c == '\n':
                                        self.lines += 1
                                self.forward += 1
                                self.lexeme_begin = self.forward
                               
                                c = self.input[self.lexeme_begin]
                                #print("Found space!")
                        
                        if self.input[self.forward] == EOF:
                                return EOF
                        token = self.GetKeyword()

                        if token is not False:
                                self.tokens.append(token)
                                self.lexeme_begin = self.forward
                                return token
                        token = self.GetRelop()
                        if token is not False:
                                self.tokens.append(token)
                                self.lexeme_begin = self.forward
                                return token
                        token = self.GetId()
                        print("IDS")
                        if token is not False:
                                self.tokens.append(token)
                                self.lexeme_begin = self.forward
                                return token
                        token = self.GetNumber()
                        print("NUMS")
                        if token is not False:
                                self.tokens.append(token)
                                self.lexeme_begin = self.forward
                                return token
                        token = self.GetQuotes()
                        if token is not False:
                                self.tokens.append(token)
                                self.lexeme_begin = self.forward
                                return token

                        token = self.GetOperator()
                        if token is not False:
                                self.tokens.append(token)
                                self.lexeme_begin = self.forward
                                return token

                        if self.NextChar() == ';':
                                token = Token(';')
                                token.attribute = ENDSTMT
                                self.tokens.append(token)
                                self.lexeme_begin = self.forward
                                return token
                        
                        self.lexeme_begin = self.forward
                        print("Error at '%s'" % self.input[self.lexeme_begin:])
                        exit(0)
                        return EOF
                        
                else:
                        print("No lexemes left!")
                        return EOF
                        
        def GetOperator(self):
                retToken = Token(OPERATOR)
                c = self.NextChar()
                print(c)
                if c == '=':
                        retToken.attribute = SET
                elif c == '*':
                        add = self.NextChar()
                        retToken.attribute = MULT
                        if add  == '=':
                                retToken.attribute = MUSET
                        else:
                                self.Retract()
                elif c == '+':
                        add = self.NextChar()
                        retToken.attribute = PLUS
                        if add == '=':
                                retToken.attribute = PLSET
                        else:
                                self.Retract()
                elif c == '-':
                        add = self.NextChar()
                        retToken.attribute = MINUS
                        if add == '=':
                                retToken.attribute = MISET
                        else:
                                self.Retract()
                   
                        
                elif c == '/':
                        add = self.NextChar()
                        retToken.attribute = DIV
                        if add == '=':
                                retToken.attribute = DISET
                        else:
                                self.Retract()

                elif c == '%':
                        add = self.NextChar()
                        retToken.attribute = MOD
                        if add == '=':
                                retToken.attribute = MOSET
                        else:
                                self.Retract()
                elif c == '.':
                        retToken.attribute = DOT
                elif c == ',':
                        retToken.attribute = ZP
                elif c == '>':
                        add = self.NextChar()
                        if add == '>':
                                retToken.attribute = SHR
                        else:
                                self.Retract()
                            
                elif c == '<':
                        add = self.NextChar()
                        if add == '<':
                                retToken.attribute = SHL
                        else:
                                self.Retract()
                            
                else:
                        self.Retract()
                        self.Fail()
                        return False

                return retToken
                        
                   
                   

        def GetQuotes(self):
                c = self.NextChar()
                retToken = Token("Quote")

                if c == '(':
                        retToken.attribute = OPRQ
                elif c == ')':
                        retToken.attribute = CLRQ
                elif c == '{':
                        retToken.attribute = OPFQ
                elif c == '}':
                        retToken.attribute = CLFQ
                elif c == '[':
                        retToken.attribute = OPSQ
                elif c == ']':
                        retToken.attribute = CLFQ
                else:
                        self.Retract()
                        #self.Fail()
                        return False
                return retToken
        def GetNumber(self):
                retToken = Token(NUMBER)
                match = NUM_RE.match(self.input[self.forward:])
                if match is not None:
                        retToken.attribute = NUM
                        print("found num!%s" % match.group(2))
                        
                        val = int(match.group(1))
                        if match.group(2) is not None:
                                val = float(match.group(1) + match.group(2))
                        if match.group(3) is not None:
                                val *= 10**(int(match.group(3)[1:]))

                        retToken.value = val
                        print(retToken.value)
                        end = max(match.end(1), match.end(2), match.end(3))
                        self.forward += end
                        return retToken
                self.Fail()
                return False

        def NextChar(self):
                self.forward += 1
                return self.input[self.forward-1]

        def GetKeyword(self):
                state = 0
                retToken = Token(RESERVED)
                part = self.input[self.forward: self.forward + 10]

                for key, regexp in KEYWORDS.items():
                        match = regexp.match(part)
                        if match is not None:
                                
                                retToken.attribute = key
                                self.forward += match.end(1)
                                return retToken

                self.Fail()
                return False
#       
        def GetId(self):
                retToken = Token(SYMBOL)
                match = ID_RE.match(self.input[self.forward:])
                if match is not None:
                        retToken.attribute = ID
                        
                        retToken.value = match.string[0:match.end(1)]
                        self.forward += match.end(1)
                        return retToken
                self.Fail()
                return False


        def Retract(self):
                self.forward -= 1


        def GetRelop(self):
                retToken = Token(RELOP)
                state = 0
                #ipdb.set_trace()
                while True:
                    if state == 0:
                            c = self.NextChar()
                            if c == '<':
                                    state = 1
                            elif c == '=':
                                    state = 5
                            elif c == '>':
                                    state = 6
                            elif c == '!':
                                    state = 2
                            else:
                                    self.Fail()
                                    return False


                    elif state == 1:
                            c = self.NextChar()
                            if c == '=':
                                    retToken.attribute = LE
                                    return retToken
                            elif c == '<':
                                    self.Fail()
                                    return False
                            else:
                                    self.Retract()
                                    retToken.attribute = LT
                                    return retToken
                    elif state == 2:
                            c = self.NextChar()
                            if c == '=':
                                    retToken.attribute = NE
                                    print("Found NotEQ")
                                    return retToken

                            else:
                                    self.Fail()
                                    return False
                                    
                    elif state == 5:
                            c = self.NextChar()
                            if c == '=':
                                    retToken.attribute = EQ
                                    return retToken
                            else:
                                    self.Fail()
                                    return False
                    elif state == 6:
                            c = self.NextChar()
                            if c == '=':
                                    retToken.attribute = GE
                                    return retToken
                            
                            elif c == '>':
                                    self.Fail()
                                    return False
                            else:
                                    self.Retract()
                                    retToken.attribute = GT
                                    return retToken
        def Fail(self):
                self.forward = self.lexeme_begin
                #print('Failed at %s' % self.input[self.lexeme_begin: self.lexeme_begin + 10])
    
#simple hello world
if __name__ == '__main__':
        in_string = sys.argv[1]
        print("Lexing %s" % in_string)
        if os.path.isfile(in_string):
                try:
                        in_string = open(in_string, 'r').read()
                except Exception as e:
                        print(e)
                        exit(0)
        
        lex = Lexer(in_string)
        tok = lex.GetNextToken()
        print tok.name + ', ' + str(tok.attribute)
        while tok != EOF:
                
                tok = lex.GetNextToken()
                if tok == EOF:
                        print("EOF met. ")
                        break
                print tok.name + ', ' + str(tok.attribute)
                       
            
        #f = lex.DenyFunc(sys.argv[1])
        print([token.name for token in lex.tokens])
        print(in_string)
