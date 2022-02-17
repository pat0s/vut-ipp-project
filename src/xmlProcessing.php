<?php

declare(strict_types=1);

class XMLFileWriter{

    private $order;
    private $xml;

    /**
	 * Constructor
	 */
    public function XMLFileWriter()
    {
        $this->order = 1;
        $this->xml = new XMLWriter();
        $this->xml->openMemory();
        $this->xml->startDocument('1.0', 'UTF-8');

        // Program tag
        $this->xml->startElement('program');
        $this->xml->writeAttribute('language', 'IPPCode22');
    }

    /**
	 * Convert an Array to XML
	 * @param string $opcode - name an operation
	 */
    public function addInstruction($opcode)
    {
        $this->xml->startElement('instruction');
        $this->xml->writeAttribute('order', strval($this->order++));
        $this->xml->writeAttribute('opcode', strtoupper($opcode));
    }

    /**
	 * Convert an Array to XML
	 * @param string $n - order of the argument
	 * @param string $type - argument's type
	 * @param string $value - value of the argument
	 */
    public function addArg($n, $type, $value)
    {
        $this->xml->startElement('arg'.$n);
        $this->xml->writeAttribute('type', $type);
        $this->xml->text($value);
        $this->xml->endElement();
    }

    /**
	 * Close XML element's tag
	 */
    public function endElement()
    {
        $this->xml->endElement();
    }

    /**
	 * Close program tag and end document
	 */
    public function endXMLBody()
    {
        $this->xml->endElement();
        
        $this->xml->endDocument();
        file_put_contents('output.xml', $this->xml->outputMemory());
    }

}
?>