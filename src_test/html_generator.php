<?php
/**
 * Project: IPP project, part 2
 * @file html_generator.php
 * 
 * @brief HTML generator for website with test results
 * @author Patrik Sehnoutek, xsehno01
 */


 /**
 * Class for generating website source code
 */
class HTMLgenerator
{
    private static $pageCode = "";
    private static $passedTests = "";
    private static $failedTests = "";
    private static $tests = "";
    private static $folderName = "";

    private static $header =' <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>IPP project 2022</title>

        <style>
            *{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: Arial, Helvetica, sans-serif;
            }

            #head{
                position: relative;
                top:0;
                width: 100%;
                height: 15vh;
                background-color: #CCC;
                box-shadow: 5px 5px 5px #DDD;
                display: flex;
                justify-content: center;
                align-items: center;
                flex-wrap: wrap;
                flex-direction: column;
                row-gap: 2vh;
            }

            #mainBody{
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
            }

            #numberOfCorrect{
                display: flex;
                width: 100%;
                justify-content: center;
                flex-wrap: wrap;
                flex-direction: column;
                align-items: center;
                height: 20vh;
                row-gap: 1vh;
            }

            #numberOfCorrect meter{
                width: 15%;
            }

            .testFile{
                width: 60%;
                left: 20%;
                height: 40vh;
                display: flex;
                justify-content: center;
                flex-direction: row;
                flex-wrap: wrap;
                align-items: center;
                margin-bottom: 5vh;
            }

            .testFile h2{
                width: 100%;
                text-align: center;
                margin-bottom: 1%;
            }

            .correct, .incorrect{
                width: 45%;
                height: 90%;
                display: flex;
                flex-direction: column;
                align-items: center;
                overflow: auto;
                padding-top: 3vh;
                padding-bottom: 2vh;
            }

            .correct{
                background-color: rgb(63, 248, 91);
                border-bottom-left-radius: 20px;
                border-top-left-radius: 20px;
                
            }
            .incorrect{
                border-bottom-right-radius: 20px;
                border-top-right-radius: 20px;
                background-color: rgb(255, 71, 71);
            }

            .correct div, .incorrect div{
                width: 90%;
                line-height: 1.5em;
                left: 5%
            }

        </style>
    </head>';

    private static $bodyStart = '<body>
    <div id="head">
        <h1>IPP project 2022</h1>
        <div>Created by Patrik Sehnoutek - xsehno01</div>
        
    </div>';

    private static $bodyEnd = '    </div>
    </body>
    </html>';
    
    /**
     * @brief Generates head tag and CSS
     */
    public static function generateHeader()
    {
        self::$pageCode = self::$pageCode.self::$header;
    }

    /**
     * @brief Generates start of body tag
     */
    public static function generateStartBody()
    {
        self::$pageCode = self::$pageCode.self::$bodyStart;
    }

    /**
     * @brief Generates test results
     * 
     * @param passed Number of passed tests
     * @param all Number of all tests
     */
    public static function generateEndBody($passed, $all)
    {
        self::$pageCode = self::$pageCode.'<div id="mainBody"><div id="numberOfCorrect"><h2>Correct: '.$passed.'/'.$all.'</h2><meter value="'.$passed.'" min="0" max="'.$all.'"></meter></div>'.self::$tests.self::$bodyEnd;
    }

    /**
     * @brief saves folder name to class attribute
     * 
     * @param folderName Name of a folder
     */
    public static function addFolder($folderName)
    {
        self::$folderName = $folderName;
    }

    /**
     * @brief Adds a test to passed or failed tests in the folder
     * 
     * @param fileName Name of a file
     * @param passed true/false
     */
    public static function addTest($fileName, $passed)
    {
        if ($passed)
        {
            self::$passedTests = self::$passedTests.'<div>'.$fileName.'</div>';
        }
        else
        {
            self::$failedTests = self::$failedTests.'<div>'.$fileName.'</div>';
        }
    }
    
    /**
     * @brief Generates source code for one folder
     */
    public static function generateFolder()
    {
        self::$tests = self::$tests.'<div class ="testFile"><h2>'.self::$folderName.'</h2><div class="correct">'.self::$passedTests.'</div>'.'<div class="incorrect">'.self::$failedTests.'</div></div>';
        self::$passedTests = "";
        self::$failedTests = "";
    }

    /**
     * @brief Prints website source code to stdin
     */
    public static function generateWebpage()
    {
        echo self::$pageCode;
    }

}
