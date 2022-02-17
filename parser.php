<?php

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

    // TODO delete
    exit(0);
}

function createXMLBody($xml)
{
    $xml->openMemory();
    $xml->startDocument('1.0', 'UTF-8');

    // program tag
    $xml->startElement('program');
    $xml->writeAttribute('language', 'IPPCode22');
}

function addInstruction($xml, &$order, $opcode)
{
    $xml->startElement('instruction');
    $xml->writeAttribute('order', $order++);
    $xml->writeAttribute('opcode', strtoupper($opcode));
}

function addArg($xml, $n, $type, $value)
{
    $xml->startElement('arg'.$n);
    $xml->writeAttribute('type', $type);
    $xml->text($value);
    $xml->endElement();
}

function endElement($xml)
{
    $xml->endElement();
}

function endXMLBody($xml)
{
    // end program tag
    $xml->endElement();
    
    // end document
    $xml->endDocument();
    file_put_contents('output.xml', $xml->outputMemory());
}



loadArguments();
$order = 1;
$xml = new XMLWriter();
createXMLBody($xml);
addInstruction($xml, $order, "pushs");
addArg($xml, 1, 'string', "GF@ahoj");
endElement($xml);
endXMLBody($xml);




?>