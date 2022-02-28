<?php

declare(strict_types=1);

class XMLFileWriter{

    private static $order;
    private static $xml;

    /**
	 * Constructor
	 */
    public static function XMLFileWriter()
    {
        self::$order = 1;
        self::$xml = new XMLWriter();
        self::$xml->openMemory();
        self::$xml->startDocument('1.0', 'UTF-8');

        // Program tag
        self::$xml->startElement('program');
        self::$xml->writeAttribute('language', 'IPPcode22');
    }

    /**
	 * Convert an Array to XML
	 * @param string $opcode - name an operation
	 */
    public static function addInstruction($opcode)
    {
        self::$xml->startElement('instruction');
        self::$xml->writeAttribute('order', strval(self::$order++));
        self::$xml->writeAttribute('opcode', strtoupper($opcode));
    }

    /**
	 * Convert an Array to XML
	 * @param string $n - order of the argument
	 * @param string $type - argument's type
	 * @param string $value - value of the argument
	 */
    public static function addArg($n, $type, $value)
    {
        self::$xml->startElement('arg'.$n);
        self::$xml->writeAttribute('type', $type);
        self::$xml->text($value);
        self::$xml->endElement();
    }

    /**
	 * Close XML element's tag
	 */
    public static function endElement()
    {
        self::$xml->endElement();
    }

    /**
	 * Close program tag and end document
	 */
    public static function endXMLBody()
    {
        self::$xml->endElement();
        
        self::$xml->endDocument();
		fwrite(STDOUT, self::$xml->flush());
    }
}
?>
