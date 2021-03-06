<?php
/**
 * Project: IPP project, part 2
 * @file test.php
 * 
 * @brief Tester for parser and interpret
 * @author Patrik Sehnoutek, xsehno01
 */


include "src_test/html_generator.php";

$path = './';
$recursive = false;
$parser = './parse.php';
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

// Print help message
if (array_key_exists('help', $args) || array_key_exists('h', $args))
{
    if (count($args) != 1)
    {
        fprintf(STDERR, "ERROR: Wrong argument/-s");
        exit(10);
    }

    print("Script test.php description\n");
    print("Usage:   php test.php [option|options]\n");
    print("Options:\n");
    print("     -h, --help                  print help and exit program\n");
    print("     -d, --directory=path        tests directory\n");
    print("     -r, --recursive             recursively search for tests in directory\n");
    print("     -p, --parse-script=file     parser script, default ./parse.php\n");
    print("     -i, --int-script=file       interpret script, default ./interpret.py\n");
    print("     --parse-only                test only parser\n");
    print("     --int-only                  test only interpret\n");
    print("     -j, --jexampath=fir         path to directory containing jexaxml.jar\n");
    print("     -n, --noclean               do not remove temporary files\n");
    exit(0);
}

// Check arguments
if (array_key_exists('directory', $args) || array_key_exists('d', $args))
{
    $path = isset($args['d']) ? './'.$args['d'] : './'.$args['directory'];
    if ($path[-1] != '/') $path = $path.'/';

    check_file($path);
}

if (array_key_exists('recursive', $args) || array_key_exists('r', $args))
{
    $recursive = true; 
}

if (array_key_exists('parse-script', $args) || array_key_exists('p', $args))
{
    $parser = isset($args['p']) ? './'.$args['p'] : './'.$args['parse-script'];
}

if (array_key_exists('int-script', $args) || array_key_exists('i', $args))
{
    $interpret = isset($args['i']) ? './'.$args['i'] : './'.$args['int-script'];
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

if (array_key_exists('jexampath', $args) || array_key_exists('j', $args))
{
    $jexamdir = isset($args['j']) ? $args['j'] : $args['jexampath'];
    if ($jexamdir[-1] != '/') $jexamdir = $jexamdir.'/';
}

if (array_key_exists('noclean', $args))
{
    $cleanTmp = false;
}

$jexamexe = $jexamdir.'jexamxml.jar';
check_file($jexamexe);

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
    $testName = preg_replace("/^(\..*\/)(.+)\.src$/", "\\2", $file);
    $testDir = preg_replace("/^(\..*\/)(.+)\.src$/", "\\1", $file);

    if (!array_key_exists($testDir, $tests))
    {
        $tests[$testDir] = [];

    }
    array_push($tests[$testDir], $testName);
}
array_multisort($tests);

$allCount = 0;
$successful = 0;

HTMLgenerator::generateHeader();
HTMLgenerator::generateStartBody();

// Execute tests
foreach($tests as $dirName => $dir)
{
    HTMLgenerator::addFolder($dirName);

    foreach($dir as $fileName)
    {
		$allCount++;
        $oldSuccessful = $successful;
		
		$srcFile = $dirName.$fileName.'.src';
        $rcFile = $dirName.$fileName.'.rc';
        $inFile = $dirName.$fileName.'.in';
        $outFile = $dirName.$fileName.'.out';
        $myOutFile = $dirName.$fileName.'.my_out';
		$diffFile = './diffs.xml';
		$myXMLFile = $dirName.$fileName.'.xml';

        // Missing files
        if (!file_exists($inFile))
        {
            create_file($inFile, "");
        }
        if (!file_exists($outFile))
        {
            create_file($outFile, "");
        }
        if (!file_exists($rcFile))
        {
            create_file($rcFile, "0");
        }

        // Parser only
        if ($parserOnly)
        {
            check_file($parser);

            unset($output);
            unset($exitCode);
            exec('php8.1 '.$parser.' < '.$srcFile.' > '.$myOutFile.' 2> /dev/null', $output, $exitCode);

			$file = fopen($rcFile, 'r');
			$rc = fgets($file);
			fclose($file);

			if ($exitCode == intval( $rc ))
            {
                if ($exitCode == 0)
                {
                    unset($output);
                    unset($exitCode);
                    exec('java -jar '.$jexamexe.' '.$outFile.' '.$myOutFile.' '.$diffFile.' '.' /D '.$jexamdir.'options', $output, $exitCode);
                    
                    if ($exitCode == 0) $successful++;
                }
                else
                {
                    $successful++;
                }
            }
        }
        // Interpret only
        else if ($interpretOnly)
        {
            check_file($interpret);

            unset($output);
            unset($exitCode);
            exec('python3.8 '.$interpret.' --source='.$srcFile.' --input='.$inFile.' > '.$myOutFile.' 2> /dev/null', $output, $exitCode);
            
            $file = fopen($rcFile, 'r');
			$rc = fgets($file);
			fclose($file);

			if ($exitCode == intval( $rc ))
            {
                if ($exitCode == 0)
                {
                    unset($output);
                    unset($exitCode);
                    exec('diff '.$outFile.' '.$myOutFile.' 2> /dev/null', $output, $exitCode);
                    
                    if ($exitCode == 0) $successful++;
                }
                else
                {
                    $successful++;
                }
            }

        }
        // Both
        else{
            check_file($parser);
            check_file($interpret);

            unset($output);
            unset($exitCode);
            exec('php8.1 '.$parser.' < '.$srcFile.' > '.$myXMLFile.' 2> /dev/null', $output, $exitCode);

			$file = fopen($rcFile, 'r');
			$rc = fgets($file);
			fclose($file);

            if ($exitCode == 0)
            {
                unset($output);
                unset($exitCode);
                exec('python3.8 '.$interpret.' --source='.$myXMLFile.' --input='.$inFile.' > '.$myOutFile.' 2> /dev/null', $output, $exitCode);
                
                if ($exitCode == intval( $rc ))
                {
                    if ($exitCode == 0)
                    {
                        unset($output);
                        unset($exitCode);
                        exec('diff '.$outFile.' '.$myOutFile.' 2> /dev/null', $output, $exitCode);
                        
                        if ($exitCode == 0) $successful++;
                    }
                    else
                    {
                        $successful++;
                    }
                }
            }
            else if ($exitCode == intval( $rc ))
            {
                $successful++;
            }
        }

        // Remove tmp files
        if ($cleanTmp)
        {
            exec('rm -f '.$diffFile.' '.$myOutFile.' '.$myXMLFile);
        }

        HTMLgenerator::addTest($fileName, boolval($successful-$oldSuccessful));
    }

    HTMLgenerator::generateFolder();
 
}

// Close body tag and generate print website source code to stdin
HTMLgenerator::generateEndBody($successful, $allCount);
HTMLgenerator::generateWebpage();

// Create files with content
function create_file($fileName, $content)
{
    $file = fopen($fileName, 'w');
    fwrite($file, $content);
    fclose($file);
}

// Check if file exists
function check_file($fileName)
{
    if (!file_exists($fileName))
    {
        fprintf(STDERR, "ERROR: File does not exist!");
        exit(41);
    }
}

?>
