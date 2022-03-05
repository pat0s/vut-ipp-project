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
        
        # TODO: remove
        for i in range(len(self.instructionsArray)):
            print(self.instructionsArray[i].opcode, ":", self.instructionsArray[i].types, "->", self.instructionsArray[i].args)
        print()
        
        print("[+] Save labels, check opcode sequence")


interpret = Interpret()
interpret.load_args()
interpret.load_source_code()


########################## TESTS ##########################

# TESTS for frames
# frame = Frames()
# frame.create_frame()
# frame.add_var("ahoj", "TF")
# print("LF:", frame.framesStack)
# print("TF:", frame.tmpFrame)
# frame.push_frame()
# frame.add_var("cau", "LF")
# print("LF:", frame.framesStack[-1])
# print("TF:", frame.tmpFrame)

# print("GF:", frame.globalFrame)
# frame.add_var("global", "GF")
# print("GF:", frame.globalFrame)
# print(frame.find_var("ahoj", "TF"))
# print(frame.find_var("global", "GF"))
# print(frame.find_var("global", "TF"))