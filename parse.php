<?php

include "src/xmlProcessing.php";

ini_set('display_errors', 'stderr');

/**
 * Class for parsing IPPcode22 source code
 */
class InstructionParser
{
    // instruction
    private $opcode;
    // instruction's arguments
    private $args = [];
    // header
    public $firstLine = true;

    /**
     * @brief Checks lexical and syntactical rules
     * 
     * @param Array of separated items
     */
    public function checkSyntax($separatedItems)
    {
        if ($this->firstLine)
        {
            if (empty($separatedItems))
            {
                fprintf(STDERR, "ERROR: Missing header!");
                exit(21);
            }
            else if ((count($separatedItems) == 1) && (strtoupper($separatedItems[0]) == ".IPPCODE22"))
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

        if ($this->checkItemsCount($separatedItems) == false)
        {
            fprintf(STDERR, "ERROR: Lexical or syntax!");
            exit(23);
        }

        if ($this->processArgs($separatedItems) == false)
        {
            fprintf(STDERR, "ERROR: Lexical or syntax!");
            exit(23);
        }
    }

    /**
     * @brief Checks number of instruction's arguments
     * 
     * @param Array of separated items
     * @return true/false
     */
    private function checkItemsCount($separatedItems)
    {
        if (empty($separatedItems))
        {
            return false;
        }

        $this->opcode = strtoupper($separatedItems[0]);

        switch ($this->opcode) {
            // zero args
            case "CREATEFRAME":
            case "PUSHFRAME":
            case "POPFRAME":
            case "RETURN":
            case "BREAK":
                if (count($separatedItems) !== 1)
                {
                    return false;
                }
                $this->args = [];
                break;
            // <label>
            case "LABEL":
            case "JUMP":
            case "CALL":
                if (count($separatedItems) !== 2)
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
                if (count($separatedItems) !== 2)
                {
                    return false;
                }
                $this->args = ["symb"];
                break;
            // <var>
            case "DEFVAR":
            case "POPS":
                if (count($separatedItems) !== 2)
                {
                    return false;
                }
                $this->args = ["var"];
                break;
            // <var> <symb>
            case "MOVE":
			case "TYPE":
            case "STRLEN":
            case "INT2CHAR":
            case "NOT":
                if (count($separatedItems) !== 3)
                {
                    return false;
                }
                $this->args = ["var", "symb"];
                break;
            // <var> <type>
            case "READ":
                if (count($separatedItems) !== 3)
                {
                    return false;
                }
                $this->args = ["var", "type"];
                break;
            // <label> <symb> <symb> jumps
            case "JUMPIFEQ":
            case "JUMPIFNEQ":
                if (count($separatedItems) !== 4)
                {
                    return false;
                }
                $this->args = ["label", "symb", "symb"];
                break;
            // <var> <symb> <symb>
            case "AND":
            case "OR":
            case "LT":
            case "GT":
            case "EQ":
            case "IDIV":
            case "MUL":
            case "SUB":
            case "ADD":
            case "STRI2INT":
			case "CONCAT":
			case "GETCHAR":
			case "SETCHAR":
                if (count($separatedItems) !== 4)
                {
                    return false;
                }
                $this->args = ["var", "symb", "symb"];
                break;
            default:
                fprintf(STDERR, "ERROR: Unknown opcode!");
                exit(22);
        }

        return true;
    }

    /**
     * @brief Parses instruction and its arguments.
     * 
     * @param Array of separated items
     * @return true/false
     */
    private function processArgs($separatedItems)
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
                    if (!preg_match("/^[a-zA-Z\_\-$&%\*\!\?][0-9a-zA-Z\_\-$&%\*\!\?]*$/", $separatedItems[$pos]))
                        return false;
                    
                    XMLFileWriter::addArg($pos, $arg, $separatedItems[$pos]);
                }
                else if ($arg == "var" || ($arg == "symb" && preg_match("/^(GF|LF|TF)/", $separatedItems[$pos])))
                {
                    if (!preg_match("/^(GF|LF|TF)@[a-zA-Z\_\-$&%\*\!\?](\S*)$/", $separatedItems[$pos]))
                        return false;

                    XMLFileWriter::addArg($pos, "var", $separatedItems[$pos]);
                }
				else if($arg == "type")
				{
					if (!preg_match("/^(int|string|nil|bool)$/", $separatedItems[$pos]))
					{
						return false;	
					}
                    XMLFileWriter::addArg($pos, $arg, $separatedItems[$pos]);
				}
                else if($arg == "symb") 
                {
                    $separated = explode('@', $separatedItems[$pos], 2);
                    if (count($separated) !== 2)
                        return false;
                    
                    if ($separated[0] == 'nil')
                    {
                        if ($separated[1] !== 'nil')
                        {
                            return false;
                        }
                    }
                    else if ($separated[0] == 'string')
                    {
                        if (!preg_match("/^([^\\\\\s#]|\\\\\d{3})*$/", $separated[1]))
                        {
                            return false;
                        }
						else
						{
							preg_replace("/</", "&lt", $separated[1]);
							preg_replace("/>/", "&gt", $separated[1]);
							preg_replace("/&/", "&amp", $separated[1]);
						}
                    }
                    else if ($separated[0] == 'int')
                    {
                        if (!preg_match("/^[\-\+][1-9]+[0-9]*$|^[1-9][0-9]*$|^0$/", $separated[1]))
                        {
                            return false;
                        }
                    }
                    else if ($separated[0] == 'bool')
                    {
                        if (!preg_match("/^(true|false)$/", $separated[1]))
                        {
                            return false;
                        } 
                    }
                    else
                    {
                        return false;
                    }

                    XMLFileWriter::addArg($pos, $separated[0], $separated[1]);
                }

                $pos++;
            }
			XMLFileWriter::endElement();
        }

        return true;
    }

}

/**
 * @brief Loads and checks program arguments
 */
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

/**
* @brief Loads and processes source code from stdin
*/
function loadSourceCode()
{
    XMLFileWriter::XMLFileWriter();
    $instructionParser = new InstructionParser();
    
    while ($line = fgets(STDIN))
    {        
        // remove comments
        $line = preg_replace('/#.*/', '', $line);
        
		// replace multiple spaces with one and remove space from the end
        $line = preg_replace('/\s+/', ' ', $line);
        if (strlen($line) > 0 && $line[strlen($line)-1] == ' ')
        {
            $line = rtrim($line, ' ');
        }
        // remove space from the beginning
        if (strlen($line) > 0 && $line[0] == ' ')
        {
            $line = ltrim($line, ' ');
        }

        // only if line contains header of some code
        if (strlen($line) > 0)
        {
            $separatedItems = explode(' ', $line);
            $instructionParser->checkSyntax($separatedItems);
        }
    }
    if ($instructionParser->firstLine)
    {
        fprintf(STDERR, "ERROR: Missing header!");
        exit(21);
    }

    XMLFileWriter::endXMLBody();
}

loadArguments();
loadSourceCode();
?>
