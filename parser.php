<?php

include "src/xmlProcessing.php";

// Load and check program arguments
function loadArguments()
{
    global $argc;

    $args = getopt("", ["help"]);
    
    if ($argc == 1)
    {
        return;
    }
    else if($argc == 2)
    {
        if (array_key_exists("help", $args))
        {
            print("\nScript loads source code IPPCode22 from stdin,\n");
            print("checks lexical and syntactic correctness.\n");
            print("\nUsage:   php parser.php\n");
            print("         php parser.php --help\n");
            print("Options:\n");
            print("         --help: print help and exit program\n");
            exit(0);
        }
        else
        {
            fprintf(STDERR, "ERROR: Bad arguments");
            exit(10);
        }
    }
}

class InstructionChecker
{
    private $opcode;
    private $args = [];
    private $firstLine = true;

    public function checkSyntax($separetedItems)
    {
        if ($this->firstLine)
        {
            if (empty($separetedItems))
            {
                fprintf(STDERR, "ERROR: Missing header!");
                exit(21);
            }
            else if ((count($separetedItems) == 1) && ($separetedItems[0] == ".IPPcode22"))
            {
                $this->firstLine = false;
                return;
            }
            else
            {
                fprintf(STDERR, "ERROR: Wrong header!");
                exit(21);
            }
        }

        if ($this->checkItemsCount($separetedItems) == false)
        {
            fprintf(STDERR, "ERROR: Lexical or syntax!");
            exit(22);
        }

        if ($this->processArgs($separetedItems) == false)
        {
            fprintf(STDERR, "ERROR: Lexical or syntax!");
            exit(22);
        }

        return;
    }

    private function checkItemsCount($separetedItems)
    {
        if (empty($separetedItems))
        {
            return false;
        }

        $this->opcode = strtoupper($separetedItems[0]);

        switch ($this->opcode) {
            // zero args
            case "CREATEFRAME":
            case "PUSHFRAME":
            case "POPFRAME":
            case "RETURN":
            case "BREAK":
                if (count($separetedItems) !== 1)
                {
                    return false;
                }
                $this->args = [];
                break;
            // <label>
            case "LABEL":
            case "JUMP":
            case "CALL":
                if (count($separetedItems) !== 2)
                {
                    return false;
                }
                $this->args = ["label"];
                break;
            // <symb>
            case "EXIT":
            case "DPRINT":
            case "WRITE":
            case "PUSHS":
                if (count($separetedItems) !== 2)
                {
                    return false;
                }
                $this->args = ["symb"];
                break;
            // <var>
            case "DEFVAR":
            case "POPS":
                if (count($separetedItems) !== 2)
                {
                    return false;
                }
                $this->args = ["var"];
                break;
            // <var> <symb>
            case "TYPE":
            case "STRLEN":
            case "INT2CHAR":
                if (count($separetedItems) !== 3)
                {
                    return false;
                }
                $this->args = ["var", "symb"];
                break;
            // <var> <type>
            case "READ":
                if (count($separetedItems) !== 3)
                {
                    return false;
                }
                $this->args = ["var", "type"];
                break;
            // <label> <symb> <symb> jumps
            case "JUMPIFEQ":
            case "JUMPIFNEQ":
                if (count($separetedItems) !== 4)
                {
                    return false;
                }
                $this->args = ["label", "symb", "symb"];
                break;
            // <var> <symb> <symb>
            case "AND":
            case "OR":
            case "NOT":
            case "LT":
            case "GT":
            case "EQ":
            case "IDIV":
            case "MUL":
            case "SUB":
            case "ADD":
            case "STRI2INT":
                if (count($separetedItems) !== 4)
                {
                    return false;
                }
                $this->args = ["var", "symb", "symb"];
                break;
            default:
                return false;
        }

        return true;
    }

    private function processArgs($separetedItems)
    {
        // generate opcode instruction
        XMLFileWriter::addInstruction($this->opcode);
        
        // only opcode
        if (count($this->args) == 0)
        {
            XMLFileWriter::endElement();
        }
        else
        {
            $pos = 1;
            foreach($this->args as $arg)
            {
                if ($arg == "label")
                {
                    if (!preg_match("/^[a-zA-Z\_\-$&%\*\!\?](\S+)$/", $separetedItems[$pos]))
                        return false;
                    
                    XMLFileWriter::addArg($pos, $arg, $separetedItems[$pos]);
                }
                else if ($arg == "var" || ($arg == "symb" && preg_match("/^(GF|LF|TF)/", $separetedItems[$pos])))
                {
                    if (!preg_match("/^(GF|LF|TF)@[a-zA-Z\_\-$&%\*\!\?](\S+)$/", $separetedItems[$pos]))
                        return false;

                    XMLFileWriter::addArg($pos, $arg, $separetedItems[$pos]);
                }
                else if($arg == "symb") 
                {
                    $separeted = explode('@', $separetedItems[$pos]);
                    if (count($separeted) !== 2)
                        return false;
                    
                    if ($separeted[0] == 'nil')
                    {
                        if ($separeted[1] !== 'nil')
                        {
                            return false;
                        }
                    }
                    else if ($separeted[0] == 'string')
                    {
                        if (!preg_match("/^([^\\\\\s#]|\\\\\d{3})*$/", $separeted[1]))
                        {
                            return false;
                        }
						else
						{
							preg_replace("/</", "&lt", $separeted[1]);
							preg_replace("/>/", "&gt", $separeted[1]);
							preg_replace("/&/", "&amp", $separeted[1]);
						}
                    }
                    else if ($separeted[0] == 'int')
                    {
                        if (!preg_match("/^[\-\+][1-9]+[0-9]*$|^[1-9][0-9]*$|^0$/", $separeted[1]))
                        {
                            return false;
                        }
                    }
                    else if ($separeted[0] == 'bool')
                    {
                        if (!preg_match("/^(true|false)$/", $separeted[1]))
                        {
                            return false;
                        } 
                    }
                    else
                    {
                        return false;
                    }

                    XMLFileWriter::addArg($pos, $separeted[0], $separeted[1]);
                }

                $pos++;
            }
			XMLFileWriter::endElement();
        }

        return true;
    }

}

// Main function
function loadSourceCode()
{
    XMLFileWriter::XMLFileWriter();
    $instructionChecker = new InstructionChecker();
    
    while ($line = fgets(STDIN))
    {        
        // remove comments
        $line = preg_replace('/#.*/', '', $line);

        // replace multiple spaces with one and remove space from the end
        // TODO: remove spaces from the beginning
        $line = preg_replace('/\s+/', ' ', $line);
        if ($line[strlen($line)-1] == ' ')
        {
            $line = rtrim($line, ' ');
        }

        // only if line contains header of some code
        if (strlen($line) > 0)
        {
            $separetedItems = explode(' ', $line);
            $instructionChecker->checkSyntax($separetedItems);
        }

        // TODO: if file is empty without header
    }
	print("[+] Closing XML body");
    XMLFileWriter::endXMLBody();
}

loadArguments();
loadSourceCode();
?>
