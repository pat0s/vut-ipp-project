##
#   @file interpret.py
#
#   @brief Interprets source code and generates output
#   @author Patrik Sehnoutek, xsehno01
#

import xml.etree.ElementTree as ET
import sys, re

from src_interpret.error import ErrorMessages
from src_interpret.components import *

class Interpret:
    """Process input source code and generate output."""
    
    INSTRUCTIONS = {"MOVE" : 2,
                    "CREATEFRAME" : 0, 
                    "PUSHFRAME" : 0,
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
                    "NOT" : 2,
                    "LT" : 3,
                    "GT" : 3,
                    "EQ" : 3,
                    "IDIV" : 3,
                    "MUL" : 3,
                    "SUB" : 3,
                    "ADD" : 3,
                    "STRI2INT" : 3,
                    "CONCAT" : 3,
                    "GETCHAR" : 3,
                    "SETCHAR" : 3
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
        # read usage
        self.readUsage = 0


    def load_args(self):
        """Load and validate program arguments."""
        argv = sys.argv
        argc = len(argv)

        if argc == 1:
            ErrorMessages.exit_code(10)  
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
                ErrorMessages.exit_code(10)   
        elif argc == 3:
            r = re.compile(r"^(--source=|--input=).+$")
            files = list(filter(r.match, argv))
            
            # too many arguments
            if len(files) != 2:
                ErrorMessages.exit_code(10)
            
            for item in files:
                item = re.split(r"=", item)
                if len(item) != 2:
                    ErrorMessages.exit_code(10)
                
                if item[0] == "--source" and self.source == "STDIN":
                    self.source = item[1]
                elif item[0] == "--input" and self.input == "STDIN":
                    self.input = item[1]
                else:
                    ErrorMessages.exit_code(10)
        else:
            ErrorMessages.exit_code(10)
        
        # input and source file cannot be the same
        if self.input == self.source:
            ErrorMessages.exit_code(10)


    def load_source_code(self):
        """Load XML source code and send it to further validation."""
        tree = None

        # parse XML source
        try:
            if self.source == "STDIN":
                tree = ET.parse(sys.stdin)
            else:
                tree = ET.parse(self.source)
        except:
            ErrorMessages.exit_code(31)

        self.code = tree.getroot()
        
        self.check_XML_root()
        self.sort_instructions_by_order()
        self.check_code()
      

    def check_XML_root(self):
        """Validate XML root element and his attributes."""
        if self.code.tag != "program" or self.code.get("language") != "IPPcode22":
            ErrorMessages.exit_code(32)
    
        for k, v in self.code.attrib.items():
            if k not in ["language", "name", "description"]:
                ErrorMessages.exit_code(32)


    def sort_instructions_by_order(self):
        """Sort instructions in ascending order by attribute 'order'."""
        try:
            self.code[:] = sorted(self.code, key=lambda child: (int(child.get("order"))))
        except:
            ErrorMessages.exit_code(32)

    
    def escape_seq_to_string(self, escape_seq):
        """Convert escape sequences and XML special characters."""
        if escape_seq == "":
            return ""

        re.sub("&gt;", ">", escape_seq)
        re.sub("&lt;", "<", escape_seq)
        re.sub("&amp;", "&", escape_seq)
        re.sub("&quot;", "\"", escape_seq)
        re.sub("&apos;", "\'", escape_seq)

        res = ""
        i = 0
        while i < len(escape_seq):
            if escape_seq[i] == '\\':
                res += chr(int(escape_seq[i+1:i+4]))
                i += 3
            else:
                res += escape_seq[i]
            i += 1
        return res 


    def parse_instruction(self, tag, position):    
        """Split instrucions to opcode and arguments and save labels."""
        instruction = Instruction()
        
        try: 
            instruction.order = tag.attrib.get("order")
            instruction.opcode = tag.attrib.get("opcode").upper()
        except:
            ErrorMessages.exit_code(32)

        if instruction.opcode in self.INSTRUCTIONS:
            no_args = self.INSTRUCTIONS[instruction.opcode]
        else:
            ErrorMessages.exit_code(32)

        if len([child for child in tag.iter()]) -1 > no_args:
            ErrorMessages.exit_code(32)

        for i in range(no_args):
            try:
                arg = tag.find(f"arg{i+1}")
                type = arg.attrib.get("type")
            except:
                ErrorMessages.exit_code(32)
            
            if type == "var":
                frame, name = arg.text.split('@')
                instruction.args.append([name, frame])
            else:
                text = arg.text              
                if type == "string":
                    if text == None:
                        text = ""
                    text = self.escape_seq_to_string(text)
                
                instruction.args.append(text)
            
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
        """Validate attribute 'order' and send instruction for parsing."""
        # position of instruction in instruction list
        position = 0

        previousOrder = -1  
        for child in self.code:
            if child.tag != "instruction":
                ErrorMessages.exit_code(32)

            order = int(child.attrib.get("order"))
            if order <= 0 or order == previousOrder:
               ErrorMessages.exit_code(32)
            previousOrder = order

            self.parse_instruction(child, position)
            position += 1
        
    
    ########################################
    ######### METHODS for OPCODES ##########
    ########################################
    
    def check_var(self, varName, varFrame, checkValue=False):
        """Check var existence in the given frame."""
        var = self.frames.find_var(varName, varFrame)
        if not var:
            ErrorMessages.exit_code(54)
        if checkValue and var.value == None:
            ErrorMessages.exit_code(56)
        return var

    
    def MOVE(self, instruction : Instruction):
        dest = self.check_var(instruction.args[0][0], instruction.args[0][1])

        if instruction.types[1] == "var":     
            src = self.check_var(instruction.args[1][0], instruction.args[1][1], True)         
            dest.change_value(src.value, src.type)
        else:
            dest.change_value(instruction.args[1], instruction.types[1])

    
    def RETURN_PRG(self):
        if self.callStack:
            self.instructionCounter = self.callStack.pop()
        else:
            ErrorMessages.exit_code(56)


    def PUSHS(self, instruction):
        if instruction.types[0] == "var":
            var = self.check_var(instruction.args[0][0], instruction.args[0][1], True)
                
            self.callStack.append(var.value)
        else:
            self.callStack.append((instruction.args[0], instruction.types[0]))


    def POPS(self, instruction):
        if not self.callStack:
            ErrorMessages.exit_code(56)

        var = self.check_var(instruction.args[0][0], instruction.args[0][1]) 
        value, type = self.callStack.pop()
        var.change_value(value, type)


    def MATH_OPERATIONS(self, instruction : Instruction, operator):
        dest = self.check_var(instruction.args[0][0], instruction.args[0][1])
        res, op2 = 0, 0

        if instruction.types[1] == "var":     
            var = self.check_var(instruction.args[1][0], instruction.args[1][1], True)
            if var.type != "int":
                ErrorMessages.exit_code(53)
            res += var.value
        else:
            if instruction.types[1] != "int":
                ErrorMessages.exit_code(53)    
            res += int(instruction.args[1])

        if instruction.types[2] == "var":     
            var = self.check_var(instruction.args[2][0], instruction.args[2][1], True)
            if var.type != "int":
                ErrorMessages.exit_code(53)
            op2 = var.value
        else:
            if instruction.types[2] != "int":
                ErrorMessages.exit_code(53)           
            op2 = int(instruction.args[2])

        # choose operation
        if operator == "+":
            res += op2
        elif operator == "-":
            res -= op2
        elif operator == "*":
            res *= op2
        elif operator == "/":
            if op2 == 0:
                ErrorMessages.exit_code(57)
            res //= op2

        dest.change_value(res, "int")


    def COMPARE(self, instruction : Instruction, operator):
        dest = self.check_var(instruction.args[0][0], instruction.args[0][1])
        val1, type1, val2, type2 = "", "", "", ""

        if instruction.types[1] == "var":     
            var = self.check_var(instruction.args[1][0], instruction.args[1][1], True)
            val1, type1 = var.value, var.type
        else:  
            val1, type1 = instruction.args[1], instruction.types[1]
            if type1 == "int":
                val1 = int(val1)

        if instruction.types[2] == "var":     
            var = self.check_var(instruction.args[2][0], instruction.args[2][1], True)
            val2, type2 = var.value, var.type
        else:  
            val2, type2 = instruction.args[2], instruction.types[2]
            if type2 == "int":
                val2 = int(val2)

        res = ""
        if type1 == type2:
            if type1 == "nil" and operator != "=":
                ErrorMessages.exit_code(53)
            if operator == "<":
                res = val1 < val2
            elif operator == ">":
                res = val1 > val2
            else:
                res = val1 == val2
        elif (type1 == "nil" or type2 == "nil") and operator == "=":
            res = False
        else:
            ErrorMessages.exit_code(53)

        dest.change_value(str(res).lower(), "bool")


    def LOGICAL_OP(self, instruction : Instruction, operator):
        dest = self.check_var(instruction.args[0][0], instruction.args[0][1])
        op1, op2 = "", ""

        if instruction.types[1] == "var":     
            var = self.check_var(instruction.args[1][0], instruction.args[1][1], True)
            if var.type != "bool":
                ErrorMessages.exit_code(53)
            op1 = var.value
        else:
            if instruction.types[1] != "bool":
                ErrorMessages.exit_code(53)           
            op1 = instruction.args[1]

        if operator != "not":
            if instruction.types[2] == "var":     
                var = self.check_var(instruction.args[2][0], instruction.args[2][1], True)
                if var.type != "bool":
                    ErrorMessages.exit_code(53)
                op2 = var.value
            else:
                if instruction.types[2] != "bool":
                    ErrorMessages.exit_code(53)           
                op2 = instruction.args[2]

        res = "false"
        if operator == "not" and op1 == "false":
            res = "true"
        elif operator == "and":
            if op1 == "true" and op2 == "true":
                res = "true"
        elif operator == "or":
            if op1 == "true" or op2 == "true":
                res = "true"

        dest.change_value(res, "bool")


    def INT2CHAR(self, instruction : Instruction):
        dest = self.check_var(instruction.args[0][0], instruction.args[0][1])
        char = ""

        if instruction.types[1] == "var":     
            var = self.check_var(instruction.args[1][0], instruction.args[1][1], True)
            if var.type != "int":
                ErrorMessages.exit_code(53)
            char = var.value
        else:
            if instruction.types[1] != "int":
                ErrorMessages.exit_code(53)           
            char = instruction.args[1]

        try:
            char = chr(int(char))
        except:
           ErrorMessages.exit_code(58)

        dest.change_value(char, "string")

    
    def STRI2CHAR(self, instruction : Instruction):
        dest = self.check_var(instruction.args[0][0], instruction.args[0][1])
        string, pos = "", -1

        if instruction.types[1] == "var":     
            var = self.check_var(instruction.args[1][0], instruction.args[1][1], True)
            if var.type != "string":
                ErrorMessages.exit_code(53)
            string = var.value
        else:
            if instruction.types[1] != "string":
                ErrorMessages.exit_code(53)           
            string = instruction.args[1]

        if instruction.types[2] == "var":     
            var = self.check_var(instruction.args[2][0], instruction.args[2][1], True)
            if var.type != "int":
                ErrorMessages.exit_code(53)
            pos = var.value
        else:
            if instruction.types[2] != "int":
                ErrorMessages.exit_code(53)           
            pos = int(instruction.args[2])

        if pos < 0 or pos >= len(string):
            ErrorMessages.exit_code(58)

        res = ord(string[pos])
        dest.change_value(res, "int")

    
    # TODO: EOF
    def READ(self, instruction : Instruction):
        # check the existence of variable
        dest = self.check_var(instruction.args[0][0], instruction.args[0][1])
        
        # stdin
        if self.input == "STDIN":
            try:
                uInput = input()
            except:
                ErrorMessages.exit_code(11)
        # from file
        else:
            try:
                with open(self.input) as f:
                    fileContent = f.read().splitlines()
            except:
                ErrorMessages.exit_code(11)

            if len(fileContent) < self.readUsage + 1:
                dest.change_value("nil", "nil")
                self.readUsage += 1
                return

            uInput = fileContent[self.readUsage]
            self.readUsage += 1

        # remove a trailing newline
        uInput.rstrip("\n")
        
        # assign value according to given type
        if instruction.args[1] == "int":
            try:
                dest.change_value(int(uInput) ,"int")
            except:
                dest.change_value("nil", "nil")
        elif instruction.args[1] == "bool":
            if uInput.lower() == "true":
                dest.change_value("true", "bool")
            else:
                dest.change_value("false", "bool")
        else:
            dest.change_value(uInput, "string")

  
    def WRITE(self, instruction : Instruction):
        string = ""
        if instruction.types[0] == "var":     
            var = self.check_var(instruction.args[0][0], instruction.args[0][1], True)
            if var.type != "nil":
                string = var.value
        else:
            if instruction.types[0] != "nil":
                string = instruction.args[0]

        print(string, end="")

    
    def CONCAT(self, instruction : Instruction):
        dest = self.check_var(instruction.args[0][0], instruction.args[0][1]) 

        res = ""
        for i in range(1, 3):
            if instruction.types[i] == "var":     
                src = self.check_var(instruction.args[i][0], instruction.args[i][1], True)

                if src.type != "string":
                    ErrorMessages.exit_code(53)
                res += src.value
            else:
                if instruction.types[i] != "string":
                    ErrorMessages.exit_code(53)
                res += instruction.args[i]

        dest.change_value(res, "string") 


    def STRLEN(self, instruction : Instruction):
        dest = self.check_var(instruction.args[0][0], instruction.args[0][1])

        res = 0
        if instruction.types[1] == "var":     
            src = self.check_var(instruction.args[1][0], instruction.args[1][1], True)

            if src.type != "string":
                ErrorMessages.exit_code(53)
            res = len(src.value)
        else:
            if instruction.types[1] != "string":
                ErrorMessages.exit_code(53)
            res = len(instruction.args[1])

        dest.change_value(res, "int")


    def GETCHAR(self, instruction : Instruction):
        dest = self.check_var(instruction.args[0][0], instruction.args[0][1])
        string, pos = "", -1

        if instruction.types[1] == "var":     
            var = self.check_var(instruction.args[1][0], instruction.args[1][1], True)
            if var.type != "string":
                ErrorMessages.exit_code(53)
            string = var.value
        else:
            if instruction.types[1] != "string":
                ErrorMessages.exit_code(53)           
            string = instruction.args[1]

        if instruction.types[2] == "var":     
            var = self.check_var(instruction.args[2][0], instruction.args[2][1], True)
            if var.type != "int":
                ErrorMessages.exit_code(53)
            pos = var.value
        else:
            if instruction.types[2] != "int":
                ErrorMessages.exit_code(53)           
            pos = int(instruction.args[2])

        if pos < 0 or pos >= len(string):
            ErrorMessages.exit_code(58)

        res = string[pos]
        dest.change_value(res, "string")


    def SETCHAR(self, instruction : Instruction):
        dest = self.check_var(instruction.args[0][0], instruction.args[0][1], True)
        if dest.type != "string":
            ErrorMessages.exit_code(53)

        string, pos = "", -1
        if instruction.types[1] == "var":     
            var = self.check_var(instruction.args[1][0], instruction.args[1][1], True)
            if var.type != "int":
                ErrorMessages.exit_code(53)
            pos = var.value
        else:
            if instruction.types[1] != "int":
                ErrorMessages.exit_code(53)           
            pos = int(instruction.args[1])

        if instruction.types[2] == "var":     
            var = self.check_var(instruction.args[2][0], instruction.args[2][1], True)
            if var.type != "string":
                ErrorMessages.exit_code(53)
            string = var.value
        else:
            if instruction.types[2] != "string":
                ErrorMessages.exit_code(53)           
            string = instruction.args[2]

        if string == "" or pos < 0 or pos >= len(dest.value):
            ErrorMessages.exit_code(58)

        if pos == len(dest.value) - 1:
            res = dest.value[:pos] + string[0]
        else:
            res = dest.value[:pos] + string[0] + dest.value[pos+1:]
        dest.change_value(res, "string")


    def TYPE(self, instruction : Instruction):
        varType = ""
        if instruction.types[1] == "var":     
            tmp = self.check_var(instruction.args[1][0], instruction.args[1][1])
            
            if tmp.type:
                varType = tmp.type
        else:
            varType = instruction.types[1]

        var = self.check_var(instruction.args[0][0], instruction.args[0][1])           
        var.change_value(varType, "string")


    def check_label(self, label):
        if label not in self.labels:
            ErrorMessages.exit_code(52)

    
    def JUMP(self, label):
        self.check_label(label)
        self.instructionCounter = self.labels[label] - 1

    
    def JUMPIF(self, instruction : Instruction, equal):       
        type1, type2, value1, value2 = None, None, None, None

        self.check_label(instruction.args[0])
        
        if instruction.types[1] == "var":
            var = self.check_var(instruction.args[1][0], instruction.args[1][1], True)
            type1, value1 = var.type, var.value
        else:
            type1, value1 = instruction.types[1], instruction.args[1]
            if type1 == "int":
                value1 = int(value1)

        if instruction.types[2] == "var":
            var = self.check_var(instruction.args[2][0], instruction.args[2][1], True)
            type2, value2 = var.type, var.value
        else:
            type2, value2 = instruction.types[2], instruction.args[2]
            if type2 == "int":
                value2 = int(value2)

        if type1 == type2 or type1 == "nil" or type2 == "nil":
            if (equal and value1 == value2) or (not equal and value1 != value2):
                self.JUMP(instruction.args[0])
        else:
            ErrorMessages.exit_code(53)


    def EXIT_PRG(self, instruction : Instruction):
        if instruction.types[0] == "var":     
            var = self.check_var(instruction.args[0][0], instruction.args[0][1], True)    
            
            if var.type == "int":
                if var.value >= 0 and var.value <= 49:
                    exit(var.value)
            else:
                ErrorMessages.exit_code(53)
        else:
            if instruction.types[0] == "int":
                if int(instruction.args[0]) >= 0 and int(instruction.args[0]) <= 49:
                    exit(int(instruction.args[0]))
            else:
                ErrorMessages.exit_code(53)

        ErrorMessages.exit_code(57)


    def DPRINT(self, instruction):
        string = ""
        if instruction.types[0] == "var":     
            var = self.check_var(instruction.args[0][0], instruction.args[0][1], True)
            string = var.value
        else:
            if instruction.types[0] != "nil":
                string = instruction.args[0]

        print(string, file=sys.stderr)    

    
    def BREAK_PRG(self):
        print("Instruction counter:", self.instructionCounter, file=sys.stderr)
        print("GF:", self.frames.globalFrame, file=sys.stderr)
        print("TF:", self.frames.tmpFrame, file=sys.stderr)
        print("LF:", self.frames, file=sys.stderr)
        print("Labels list:", self.labels,file=sys.stderr)


    def interpret_code(self):
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
                self.MATH_OPERATIONS(instruction, "+")

            # SUB
            elif opcode == "SUB":
                self.MATH_OPERATIONS(instruction, "-")
            
            # MUL
            elif opcode == "MUL":
                self.MATH_OPERATIONS(instruction, "*")
            
            # IDIV
            elif opcode == "IDIV":
                self.MATH_OPERATIONS(instruction, "/")
            
            # LT
            elif opcode == "LT":
                self.COMPARE(instruction, "<")
            
            # GT
            elif opcode == "GT":
                self.COMPARE(instruction, ">")
            
            # EQ
            elif opcode == "EQ":
                self.COMPARE(instruction, "=")
            
            # AND
            elif opcode == "AND":
                self.LOGICAL_OP(instruction, "and")
            
            # OR
            elif opcode == "OR":
                self.LOGICAL_OP(instruction, "or")
            
            # NOT
            elif opcode == "NOT":
                self.LOGICAL_OP(instruction, "not")
            
            # INT2CHAR
            elif opcode == "INT2CHAR":
                self.INT2CHAR(instruction)
            
            # STR2INT
            elif opcode == "STRI2INT":
                self.STRI2CHAR(instruction)

            # READ
            elif opcode == "READ":
                self.READ(instruction)

            # WRITE
            elif opcode == "WRITE":
                self.WRITE(instruction)

            # CONCAT
            elif opcode == "CONCAT":
                self.CONCAT(instruction)

            # STRLEN
            elif opcode == "STRLEN":
                self.STRLEN(instruction)

            # GETCHAR
            elif opcode == "GETCHAR":
                self.GETCHAR(instruction)

            # SETCHAR
            elif opcode == "SETCHAR":
                self.SETCHAR(instruction)

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

            # EXIT
            elif opcode == "EXIT":
                self.EXIT_PRG(instruction)

            # DRPINT
            elif opcode == "DPRINT":
                self.DPRINT(instruction)

            # BREAK
            elif opcode == "BREAK":
                self.BREAK_PRG()

            self.instructionCounter += 1
        
        exit(0)


if __name__ == "__main__":
    interpret = Interpret()
    interpret.load_args()
    interpret.load_source_code()
    interpret.interpret_code()