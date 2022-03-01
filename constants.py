
INSTRUCTIONS = {"CREATEFRAME" : [], 
                "PUSHSFRAME" : [],
                "POPFRAME" : [],
                "RETURN" : [],
                "BREAK" : [],
                "LABEL" : ["label"],
                "JUMP" : ["label"],
                "CALL" : ["label"],
                "EXIT" : ["symb"],
                "DPRINT" : ["symb"],
                "WRITE" : ["symb"],
                "PUSHS" : ["symb"],
                "DEFVAR" : ["var"],
                "POPS" : ["var"],
                "TYPE" : ["var", "symb"],
                "STRLEN" : ["var", "symb"],
                "INT2CHAR" : ["var", "symb"],
                "READ" : ["var", "type"],
                "JUMPIFEQ" : ["label", "symb", "symb"],
                "JUMPIFNEQ" : ["label", "symb", "symb"],
                "AND" : ["var", "symb", "symb"],
                "OR" : ["var", "symb", "symb"],
                "NOT" : ["var", "symb", "symb"],
                "LT" : ["var", "symb", "symb"],
                "GT" : ["var", "symb", "symb"],
                "EQ" : ["var", "symb", "symb"],
                "IDIV" : ["var", "symb", "symb"],
                "MUL" : ["var", "symb", "symb"],
                "SUB" : ["var", "symb", "symb"],
                "ADD" : ["var", "symb", "symb"],
                "STR2INT" : ["var", "symb", "symb"]
            }



        
              

# pridat root ako atribut do triedy interpret
# order -> nie je to postupne, potreba zoradit instrukcie
# Trieda pre instrukciu
# pre kazdu instrukciu opat jej argumenty -> pomocou casu ako pri parser.php,
#       kontrolovat ich pocet
#       potom aj syntax
#       semantika ???

# co je vystupm interpretu ???