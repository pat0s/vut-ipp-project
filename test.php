<?php

$path = '.';
$recursive = false;
$parser = './parser.php';
$interpret = './interpret.py';
$parserOnly = false;
$interpretOnly = false;
$jexamdir = '/pub/courses/ipp/jexamxml/';
$cleanTmp = true;

$argc;
$argv;
$shortopts = 'h:d:r:p:i:j:n';
$longopts =  ["help", "directory", "recursive", "parse-script", "int-script", "parse-only", "int-only", "jexampath", "noclean"];
$args = getopt($shortopts, $longopts);

if (count($args) != (count($argv) - 1))
{
    fprintf(STDERR, "ERROR: Wrong argument/-s");
    exit(10);
}

// TODO: neviem, ci je potrebne osetrovat aj pocet argumentov pri tom, ked bude help
if (array_key_exists('help', $args) || array_key_exists('h', $args))
{
    print("Script test.php description\n");
    print("Usage:   php test.php [option|options]\n");
    print("Options:\n");
    print("     -h, --help                  print help and exit program\n");
    print("     -d, --directory=path        tests directory\n");
    print("     -r, --recursive             recursively search for tests in directory\n");
    print("     -p, --parse-script=file     parser script, default ./parser.php\n");
    print("     -i, --int-script=file       interpret script, default ./interpret.py\n");
    print("     --parse-only                test only parser\n");
    print("     --int-only                  test only interpret\n");
    print("     -j, --jexampath=fir         path to directory containing jexaxml.jar\n");
    print("     -n, --noclean               do not remove temporary files\n");
    exit(0);
}

if (array_key_exists('directory', $args) || array_key_exists('d', $args))
{
    $path = isset($args['d']) ? $args['d'] : $args['directory'];
}

if (array_key_exists('recursive', $args) || array_key_exists('r', $args))
{
    $recursive = true; 
}

if (array_key_exists('parse-script', $args) || array_key_exists('p', $args))
{
    $parser = $isset($args['p']) ? $args['p'] : $args['parse-script'];
}

if (array_key_exists('int-script', $args) || array_key_exists('i', $args))
{
    $$interpret = isset($args['i']) ? $args['i'] : $args['int-script'];
}

if (array_key_exists('parse-only', $args))
{
    if (!array_key_exists('int-only', $args) && !array_key_exists('int-script', $args) && !array_key_exists('i', $args))
    {
        $parserOnly = true;
    }
    else
    {
        fprintf(STDERR, "ERROR: Wrong argument/-s");
        exit(10);
    }
}
if (array_key_exists('int-only', $args))
{
    if (!array_key_exists('parse-only', $args) && !array_key_exists('parse-script', $args) && !array_key_exists('p', $args) && !array_key_exists('jexampath', $args))
    {
        $interpretOnly = true;
    }
    else
    {
        fprintf(STDERR, "ERROR: Wrong argument/-s");
        exit(10);
    }
}

if (array_key_exists('jexampath', $args))
{
    $jexamdir = $args['jexampath'];
}

if (array_key_exists('noclean', $args))
{
    $cleanTmp = false;
}


// TODO: pozor na konci nemusi byt -> /
$jexamexe = $jexamdir.'jexamxml.jar';

?>