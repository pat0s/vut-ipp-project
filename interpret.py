import xml.etree.ElementTree as ET
# for argv
import sys, re


class Interpret:
    def __init__(self):
        # Source code XML
        self.source = "STDIN"
        # Code for XML (read, ...)
        self.input = "STDIN"


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
                print("This is help")
                sys.exit(0)
            elif re.search(r"^--source=.+$", argv[1]):
                self.source = re.findall("=", argv[1])
            elif re.search(r"^--input=.+$", argv[1]):
                self.input = re.findall("=", argv[1])
            else:
                self.print_error("ERROR: Unknown combination of arguments!", 10)
        
        elif argc == 3:
            r = re.compile(r"^(--source=|--input=).+$")
            files = list(filter(r.match, argv))
            
            # Too many arguments
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
        
        # TODO input and source file cannot be the same
        #print(self.source, self.input)
              

interpret = Interpret()
interpret.load_args()