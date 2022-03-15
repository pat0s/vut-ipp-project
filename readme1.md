# Implementační dokumentace k 1. úloze do IPP 2021/2022
**Jméno a příjmení:** Patrik Sehnoutek\
**Login:** xsehno01

### Úvod ###
Skript `parse.php` je implementovaný v jazyku PHP 8.1. Jeho úlohou je vykonávať lexikálnu a syntaktickú analýzu jazyku IPPcode22.

### Implementácia ###
Prvú časť projektu som rozdelil do dvoch súborov. Hlavný skript je `parse.php` a pomocný skript `xml_processing.php` je umiestnený v adresári `src_parse/`.

**xmlProcessing.php**

Skript obsahuje jednu triedu ` XMLFileWriter()`. V triede sú implementované funkcie na tvorbu súboru XML, ktorý je výstupom prvej časti projektu. Na tvorbu XML súboru som využil rozšírenie `XMLWriter`, ktoré poskytuje potrebnú funkcionalitu na vytváranie jednotlivých XML elementov a tagov.

**parse.php**

Hlavnú časť skriptu tvorí trieda `InstructionParser`, ktorá má za úlohu analyzovať vstupný IPPcode22. Zostávajúcu časť tvoria dve funkcie `loadArguments()` a `loadSourceCode()`. Funkcia `loadArguments()` má za úlohu načítať a skontrolovať správnosť zadaných argumentov programu. Po úspešnom vykonaní nasleduje funkcia `loadSourceCode()`, ktorá zo štandardného vstupu (STDIN) načítava vstupný zdrojový kód v jazyku IPPcode22. Zdrojový kód načítava riadok po riadku. Načítaný riadok rozdelí na inštrukciu a argumenty a pošle na spracovanie triede `InstructionParser`. Komentáre a prázdne riadky sú ignorované pomocou regulárnych výrazov a neposielajú sa ďalej na spracovanie. Trieda `InstructionParser` obsahuje metódy `checkSyntax()`, `checkItemsCount()` a `processArgs()`. Pomocou nich sa skontroluje lexikálna a syntaktická analýza jednotlivých inštrukcií a jej argumentov. Na kontrolu typu inštrukcie je využité vetvenie *switch-case* a na kontrolu argumentov regulárne výrazy.