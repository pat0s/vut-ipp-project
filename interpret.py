import xml.etree.ElementTree as ET
import sys, re

from src_interpret.error import ErrorMessages
from src_interpret.components import *

class Interpret:
    INSTRUCTIONS = {"MOVE" : 2,
                    "CREATEFRAME" : 0, 
                    "PUSHSFRAME" : 0,
                    "POPFRAME" : 0,
                    "RETURN" : 0,
                    "BREAK" : 0,
                    "LABEL" : 1,
                    "JUMP" : 1,
                    "CALL" : 1,
                    "EXIT" : 1,
                    "DPRINT" : 1,
                    "WRITE" : 1,
                    "PUSHS" : 1,
                    "DEFVAR" : 1,
                    "POPS" : 1,
                    "TYPE" : 2,
                    "STRLEN" : 2,
                    "INT2CHAR" : 2,
                    "READ" : 2,
                    "JUMPIFEQ" : 3,
                    "JUMPIFNEQ" : 3,
                    "AND" : 3,
                    "OR" : 3,
                    "NOT" : 3,
                    "LT" : 3,
                    "GT" : 3,
                    "EQ" : 3,
                    "IDIV" : 3,
                    "MUL" : 3,
                    "SUB" : 3,
                    "ADD" : 3,
                    "STR2INT" : 3
                }

    def __init__(self):
        # source code XML
        self.source = "STDIN"
        # code for XML (read, ...)
        self.input = "STDIN"
        # labels list
        self.labels = {}
        # source code
        self.code = ""
        # parsed code to instructions
        self.instructionsArray = []
        # jump and call stack
        self.callStack = []
        # instruction counter
        self.instructionCounter = 0
        # frames class
        self.frames = Frames()


    def print_error(self, err_msg, err_code):
        print(err_msg, file=sys.stderr)
        exit(err_code)


    def load_args(self):
        argv = sys.argv
        argc = len(argv)

        if argc == 1:
            self.print_error("ERROR: At least one of source or input file has to be specified!", 10)
        
        elif argc == 2:
            if argv[1] == "--help":
                print("\nScript loads XML representation of source code")
                print("interprets it and generates output.")
                print("\nUsage:")
                print("         python3 interpret.py")
                print("         python3 interpret.py --help")
                print("         python3 interpret.py [--source=file] [--input=file]")
                print("Options:")
                print("         --help          print help and exit program")
                print("         --source=file   input source code XML")
                print("         --input=file    file with inputs for interpret")
                sys.exit(0)
            elif re.search(r"^--source=.+$", argv[1]):
                self.source = re.findall(r"(?<=\=).*", argv[1])[0]
            elif re.search(r"^--input=.+$", argv[1]):
                self.input = re.findall(r"(?<=\=).*", argv[1])[0]
            else:
                self.print_error("ERROR: Unknown combination of arguments!", 10)
        
        elif argc == 3:
            r = re.compile(r"^(--source=|--input=).+$")
            files = list(filter(r.match, argv))
            
            # too many arguments
            if len(files) != 2:
                self.print_error("ERROR: Unknown combination of arguments!", 10)
            
            for item in files:
                item = re.split(r"=", item)
                print(item)
                if len(item) != 2:
                    self.print_error()
                
                if item[0] == "--source" and self.source == "STDIN":
                    self.source = item[1]
                elif item[0] == "--input" and self.input == "STDIN":
                    self.input = item[1]
                else:
                    self.print_error("ERROR: Multiple same arguments", 10)
        else:
            self.print_error("ERROR: Unknown combination of arguments!", 10)
        
        # TODO: input and source file cannot be the same


    def load_source_code(self):
        tree = None

        # parse XML source
        try:
            if self.source == "STDIN":
                tree = ET.parse(sys.stdin)
            else:
                tree = ET.parse(self.source)
        except:
            self.print_error("ERROR: Cannot parse XML source code!", 31)

        self.code = tree.getroot()
        
        print("[+] Parsing OK")
        self.check_XML_root()
        self.sort_instructions_by_order()
        self.check_code()
      

    def check_XML_root(self):
        # check root tag
        if self.code.tag != "program" or self.code.get("language") != "IPPcode22":
            ErrorMessages.exit_code(32)
    
        print("[+] Root tag OK")

        # TODO: name a description v root elemente 
        print("[+] Root attrib ok")


    def sort_instructions_by_order(self):
        # sort by order
        try:
            self.code[:] = sorted(self.code, key=lambda child: (int(child.get("order"))))
        except:
            ErrorMessages.exit_code(32)

        print("[+] Sorting ...")

    def parse_instruction(self, tag, position):    
        # instruction instance
        instruction = Instruction()
        
        try: 
            instruction.order = tag.attrib.get("order")
            instruction.opcode = tag.attrib.get("opcode").upper()
        except:
            ErrorMessages.exit_code(32)

        no_args = self.INSTRUCTIONS[instruction.opcode]

        for i in range(no_args):
            arg = tag.find(f"arg{i+1}")
            type = arg.attrib.get("type")
            if type == "var":
                frame, name = arg.text.split('@')
                instruction.args.append([name, frame])
            else:
                instruction.args.append(arg.text)
            instruction.types.append(type)
            instruction.no_args += 1

        self.instructionsArray.append(instruction)

        # create list of labels
        if instruction.opcode == "LABEL":
                label_name = tag.find("arg1").text
                if label_name in self.labels:
                    ErrorMessages.exit_code(52)
                else:
                    self.labels[label_name] = position


    def check_code(self):
        # position of instruction in instruction list
        position = 0

        # check order and save labels
        previous_order = -1  
        for child in self.code:
            order = int(child.attrib.get("order"))
            if order <= 0 or order == previous_order:
               ErrorMessages.exit_code(32)
            previous_order = order

            self.parse_instruction(child, position)
            position += 1
        
        print("[+] Save labels, check opcode sequence")

    
    ########################################
    ######## FUNCTIONS for OPCODES #########
    ########################################
    
    def RETURN_PRG(self):
        if self.callStack:
            self.instructionCounter = self.callStack.pop()
        else:
            ErrorMessages.exit_code(56)


    def PUSHS(self, instruction):
        if instruction.types[0] == "var":
            var = self.frames.find_var(instruction.args[0][0], instruction.args[0][1])
            if not var:
                ErrorMessages.exit_code(54)
                
            self.callStack.append(var.value)
        else:
            self.callStack.append((instruction.args[0], instruction.types[0]))


    def POPS(self, instruction):
        if not self.callStack:
            ErrorMessages.exit_code(56)
            
        var = self.frames.find_var(instruction.args[0][0], instruction.args[0][1])
        if not var:
            ErrorMessages.exit_code(54)
        value, type = self.callStack.pop()
        var.change_value(value, type)

    
    def WRITE(self, instruction : Instruction):
        string = ""
        if instruction.types[0] == "var":     
            var = self.frames.find_var(instruction.args[0][0], instruction.args[0][1])
            
            if not var:
                ErrorMessages.exit_code(54)         
            if var.value == None:
                ErrorMessages.exit_code(56)
            
            string = var.value
        else:
            if instruction.types[0] != "nil":
                string = instruction.args[0]

        print(string, end="")  #, file=sys.stdout)

    
    def MOVE(self, instruction : Instruction):
        scr = None
        dest = self.frames.find_var(instruction.args[0][0], instruction.args[0][1])
        
        if not dest:
            ErrorMessages.exit_code(54)

        if instruction.types[1] == "var":     
            src = self.frames.find_var(instruction.args[1][0], instruction.args[1][1])
            
            if not src:
                ErrorMessages.exit_code(54)         
            if src.value == None:
                ErrorMessages.exit_code(56)
            
            dest.change_value(src.value, src.type)
        else:
            dest.change_value(instruction.args[1], instruction.types[1])

    
    def TYPE(self, instruction : Instruction):
        varType = ""
        if instruction.types[1] == "var":     
            var = self.frames.find_var(instruction.args[1][0], instruction.args[1][1])
            
            if not var:
                ErrorMessages.exit_code(54)         
            if var.type:
                varType = var.type
        else:
            if instruction.types[1] != "nil":
                varType = instruction.types[1]

        var = self.frames.find_var(instruction.args[0][0], instruction.args[0][1])
        if not var:
            ErrorMessages.exit_code(54)         
            
        var.change_value(varType, "string")

    
    
    def JUMP(self, label):

        if label not in self.labels:
            ErrorMessages.exit_code(52)

        self.instructionCounter = self.labels[label] - 1

    
    def JUMPIF(self, instruction : Instruction, equal):
        type1, type2, value1, value2 = None, None, None, None
        if instruction.types[1] == "var":
            var = self.frames.find_var(instruction.args[1][0], instruction.args[1][1])
            
            if not var:
                ErrorMessages.exit_code(54)

            if var.type == "nil":
                self.JUMP(instruction.args[0])
                return
            type1, value1 = var.type, var.value
        else:
            if instruction.types[1] == "nil":
                self.JUMP(instruction.args[0])
                return
            type1, value1 = instruction.types[1], instruction.args[1]

        if instruction.types[2] == "var":
            var = self.frames.find_var(instruction.args[2][0], instruction.args[2][1])
            
            if not var:
                ErrorMessages.exit_code(54)

            if var.type == "nil":
                self.JUMP(instruction.args[0])
                return
            type2, value2 = var.type, var.value
        else:
            if instruction.types[2] == "nil":
                self.JUMP(instruction.args[0])
                return
            type1, value1 = instruction.types[2], instruction.args[2]

        if type1 == type2:
            if (equal and value1 == value2) or (not equal and value1 != value2):
                self.JUMP(instruction.args[0])


    def EXIT_PRG(self, instruction : Instruction):
        if instruction.types[0] == "var":     
            var = self.frames.find_var(instruction.args[0][0], instruction.args[0][1])
            
            if not var:
                ErrorMessages.exit_code(54)         
            
            if var.type == "int" and var.value >= 0 and var.value <= 49:
                exit(var.value)
        else:
            if instruction.types[0] == "int" and int(instruction.args[0]) >= 0 and int(instruction.args[0]) <= 49:
                exit(int(instruction.args[0]))

        ErrorMessages.exit_code(57)


    def DPRINT(self, instruction):
        string = ""
        if instruction.types[0] == "var":     
            var = self.frames.find_var(instruction.args[0][0], instruction.args[0][1])
            
            if not var:
                ErrorMessages.exit_code(54)         
            if var.value == None:
                ErrorMessages.exit_code(56)
            
            string = var.value
        else:
            if instruction.types[0] != "nil":
                string = instruction.args[0]

        print(string, file=sys.stderr)    

    
    def BREAK_PRG(self):
        print("Instruction counter:", self.instructionCounter, file=sys.stderr)
        print("GF:", self.frames.globalFrame, file=sys.stderr)
        print("TF:", self.frames.tmpFrame, file=sys.stderr)
        #print("LF:", self.frames, file=sys.stderr)
        print("Labels list:", self.labels,file=sys.stderr)


    def interpret_code(self):
        # help variables
        while self.instructionCounter < len(self.instructionsArray):
            instruction = self.instructionsArray[self.instructionCounter]
            opcode = instruction.opcode
            
            # MOVE
            if opcode == "MOVE":
                self.MOVE(instruction)
            
            # CREATEFRAME
            elif opcode == "CREATEFRAME":
                self.frames.create_frame()
            
            # PUSHFRAME
            elif opcode == "PUSHFRAME":
                self.frames.push_frame()

            # POPFRAME
            elif opcode == "POPFRAME":
                self.frames.pop_frame()

            # DEFVAR
            elif opcode == "DEFVAR":
                self.frames.add_var(instruction.args[0][0], instruction.args[0][1])

            # CALL
            elif opcode == "CALL":
                self.callStack.append(self.instructionCounter+1)
                self.JUMP(instruction.args[0])

            # RETURN
            elif opcode == "RETURN":
                self.RETURN_PRG()
                continue

            # PUSHS
            elif opcode == "PUSHS":
                self.PUSHS(instruction)
                    
            # POPS
            elif opcode == "POPS":
                self.POPS(instruction)
            
            # ADD
            elif opcode == "ADD":
                pass
            
            # SUB
            elif opcode == "SUB":
                pass
            
            # MUL
            elif opcode == "MUL":
                pass
            
            # IDIV
            elif opcode == "IDIV":
                pass
            
            # LT
            elif opcode == "LT":
                pass
            
            # GT
            elif opcode == "GT":
                pass
            
            # EQ
            elif opcode == "EQ":
                pass
            
            # AND
            elif opcode == "AND":
                pass
            
            # OR
            elif opcode == "OR":
                pass
            
            # NOT
            elif opcode == "NOT":
                pass
            
            # INT2CHAR
            elif opcode == "INT2CHAR":
                pass
            
            # STR2INT
            elif opcode == "STR2INT":
                pass

            # READ
            elif opcode == "READ":
                pass

            # WRITE
            elif opcode == "WRITE":
                self.WRITE(instruction)

            # CONCAT
            elif opcode == "CONCAT":
                pass

            # STRLEN
            elif opcode == "STRLEN":
                pass

            # GETCHAR
            elif opcode == "GETCHAR":
                pass

            # SETCHAR
            elif opcode == "SETCHAR":
                pass

            # TYPE
            elif opcode == "TYPE":
                self.TYPE(instruction)
            
            # LABEL
            elif opcode == "LABEL":
                pass

            # JUMP
            elif opcode == "JUMP":
                self.JUMP(instruction.args[0])

            # JUMPIFEQ
            elif opcode == "JUMPIFEQ":
                self.JUMPIF(instruction, True)

            # JUMPIFNEQ
            elif opcode == "JUMPIFNEQ":
                self.JUMPIF(instruction, False)

            # JUMP
            elif opcode == "EXIT":
                self.EXIT_PRG(instruction)

            # JUMP
            elif opcode == "DPRINT":
                self.DPRINT(instruction)

            # JUMP
            elif opcode == "BREAK":
                self.BREAK_PRG()

            self.instructionCounter += 1
        
        exit(0)


interpret = Interpret()
interpret.load_args()
interpret.load_source_code()
interpret.interpret_code()
