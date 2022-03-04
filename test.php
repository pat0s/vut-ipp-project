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
$shortopts = 'hd:rp:i:j:n';
$longopts =  ["help", "directory:", "recursive", "parse-script:", "int-script:", "parse-only", "int-only", "jexampath:", "noclean"];
$args = getopt($shortopts, $longopts);

if (count($args) != (count($argv) - 1) || count($args) > 7)
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
    $parser = isset($args['p']) ? $args['p'] : $args['parse-script'];
}

if (array_key_exists('int-script', $args) || array_key_exists('i', $args))
{
    $interpret = isset($args['i']) ? $args['i'] : $args['int-script'];
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
    if ($jexamdir[-1] != '/') $jexamdir = $jexamdir.'/';
}

if (array_key_exists('noclean', $args))
{
    $cleanTmp = false;
}

$jexamexe = $jexamdir.'jexamxml.jar';

// Iterator or Recursive Iterator
$directoryIter = new RecursiveDirectoryIterator($path);
if ($recursive)
{
    $iterator = new RecursiveIteratorIterator($directoryIter);
}
else
{
    $iterator = new IteratorIterator($directoryIter);
}

$regexIter = new RegexIterator($iterator, "/^.+\.src$/");

// Load and save tests files
$tests = [];
foreach($regexIter as $file)
{
    // ^(\..*\\\\)(.+)(?=\.)\.src$, ^(\..*\\\\)(.+)\.src$ - Windows
    // ^(\..*\/)(.+)(?=\.)\.src$, ^(\..*\/)(.+)\.src$ - Linux
    $testName = preg_replace("/^(\..*\\\\)(.+)\.src$/", "\\2", $file);
    $testDir = preg_replace("/^(\..*\\\\)(.+)\.src$/", "\\1", $file);

    if (!array_key_exists($testDir, $tests))
    {
        $tests[$testDir] = [];

    }
    array_push($tests[$testDir], $testName);
}
array_multisort($tests);

// Execute tests
foreach($tests as $dirName => $dir)
{
    foreach($dir as $file)
    {
        $srcFile = $dirName.$file.'.src';
        $rcFile = $dirName.$file.'.rc';
        $inFile = $dirName.$file.'.in';
        $outFile = $dirName.$file.'.out';
        $myOutFile = $dirName.$file.'.my_out';
        
        // Parser only
        if ($parserOnly)
        {
            unset($exitCode);
            //exec('php8.1 '.$parser.' < '.$srcFile.' > '.$myOutFile, '', $exitCode);
            if ($exitCode == 0)
            {
                unset($output);
                unset($exitCode);
                //exec('java -jar'.$jexamexe.' '.$outFile.' '.$myOutFile, $output, $exitCode);
            }
        }
        // Interpret only
        else if ($interpretOnly)
        {
            unset($output);
            unset($exitCode);
            //exec('python3.8 '.$interpret.' --source='.$srcFile.' < '.$inFile.' > '.$myOutFile, '', $exitCode);
            if ($output == 0)
            {
                unset($output);
                unset($exitCode);
                //exec('diff '.$outFile.' '.$myOutFile, $output, $exitCode);   
            }
        }
        // Both
        else{

        }
    }
 
}

?>