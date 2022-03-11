##
#   @file components.py
#
#   @brief Contains classes for interpret.py
#   @author Patrik Sehnoutek, xsehno01
#

from .error import ErrorMessages


class Variable:
    """Class for variable."""
    def __init__(self, name, frame):
        self.name = name
        self.value = None
        self.type = None
        self.frame = frame

    def change_value(self, value, type):
        """Updates value and type of variable."""
        if type == "int":
            value = int(value)        
        
        self.value = value
        self.type = type


class Instruction:
    """Class for parsed instruction with arguments."""
    def __init__(self):
        self.opcode = ""
        self.order = -1
        self.args = []
        self.types = []
        self.no_args = 0


class Frames:
    """Symtable for variables.
    
    Symtable contains Temporary Frame (TF), Local Frame (LF),
    and Global Frame (GF). TF is created using opcode CREATEFRAME.
    TF become LF after using opcode PUSHSFRAME. GF is available
    during whole execution.
    """
    def __init__(self):
        self.framesStack = []
        self.globalFrame = {}
        self.tmpFrame = None

    def create_frame(self):
        """Creates new TF."""
        self.tmpFrame = {}

    def push_frame(self):
        """Saves TF to frame stack."""
        if self.tmpFrame is None:
            ErrorMessages.exit_code(55)
        
        self.framesStack.append(self.tmpFrame)
        self.tmpFrame = None

    def pop_frame(self):
        """Removes frame from frame stack and saves it as TF."""
        if not self.framesStack:
            ErrorMessages.exit_code(55)

        self.tmpFrame = self.framesStack.pop()

    def find_var(self, varName, frame) -> Variable:
        """Finds variable by its name in the given frame.
        
            :return: found variable | None
            :rtype: instance of class Variable | None
        """
        if frame == "GF":
            if varName in self.globalFrame:
                return self.globalFrame[varName]
        elif frame == "LF": 
            if not self.framesStack:
                ErrorMessages.exit_code(55)
            if varName in self.framesStack[-1]:
                return self.framesStack[-1][varName]
        elif frame == "TF":
            if self.tmpFrame == None:
                ErrorMessages.exit_code(55)
            if varName in self.tmpFrame: 
                return self.tmpFrame[varName]

        return None

    def add_var(self, varName, frame):
        """Saves variable to the given frame."""
        if self.find_var(varName, frame):
            ErrorMessages.exit_code(52)

        variable = Variable(varName, frame)
        if frame == "GF":
            self.globalFrame[varName] = variable
        elif frame == "LF":
            self.framesStack[-1][varName] = variable
        elif frame == "TF":
            self.tmpFrame[varName] = variable
