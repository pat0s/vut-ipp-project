<?php

include "src/xmlProcessing.php";

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
    private $var;
    private $type;
    private $arg;
}

loadArguments();

$xmlWriter = new XMLFileWriter();
$xmlWriter->XMLFileWriter();
$xmlWriter->addInstruction("pushs");
$xmlWriter->addArg(1, "string", "GF@ahoj");
$xmlWriter->endElement();
$xmlWriter->endXMLBody();

$instructionChecker = new InstructionChecker();


// Main function
function loadSourceCode()
{
    while ($line = fgets(STDIN))
    {       
        $separetedItems = explode(' ', $line);
        echo $separetedItems[0];
    }
}

loadSourceCode();

?>