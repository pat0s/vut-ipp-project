from .error import ErrorMessages


class Variable:
    def __init__(self, name, frame):
        self.name = name
        self.value = None
        self.type = None
        self.frame = frame

    def change_value(self, value, type):
        if type == "int":
            value = int(value)        
        
        self.value = value
        self.type = type


class Instruction:
    def __init__(self):
        self.opcode = ""
        self.order = -1
        self.args = []
        self.types = []
        self.no_args = 0


class Frames:
    def __init__(self):
        self.framesStack = []
        self.globalFrame = {}
        self.tmpFrame = None

    def create_frame(self):
        self.tmpFrame = {}

    def push_frame(self):
        if self.tmpFrame is None:
            ErrorMessages.exit_code(55)
        
        self.framesStack.append(self.tmpFrame)
        self.tmpFrame = None

    def pop_frame(self):
        if not self.framesStack:
            ErrorMessages.exit_code(55)

        self.tmpFrame = self.framesStack.pop()

    def find_var(self, varName, frame) -> Variable:
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
        if self.find_var(varName, frame):
            ErrorMessages.exit_code(52)

        variable = Variable(varName, frame)
        if frame == "GF":
            self.globalFrame[varName] = variable
        elif frame == "LF":
            self.framesStack[-1][varName] = variable
        elif frame == "TF":
            self.tmpFrame[varName] = variable
