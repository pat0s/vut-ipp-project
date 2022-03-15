# Implementační dokumentace k 2. úloze do IPP 2021/2022
**Jméno a příjmení:** Patrik Sehnoutek\
**Login:** xsehno01

## interpret.py ##
 * **jazyk:** Python 3.8
 * **úloha:** interpretácia vstupnej XML reprezentácie jazyka IPPcode22

Pomocné skripty `error.py` a `components.py` pre interpret sa nachádzajú v priečinku `src_interpret/`.

Hlavnú časť intertretu tvorí trieda `Interpret`. Jej úlohou je ošetrenie vstupných argumentov a XML reprezentácie vstupného zdrojového kódu jazyka IPPcode22. Po úspešnom skontrolovaní vstupu a programových argumentov je jej úlohou samotná interpretácia kódu a generovanie výstupu. Zdrojový kód najprv nasledovne uloží do pola: každý riadok v poli predstavuje jednu inštanciu triedy `Instruction`, ktorá v sebe zapúzdruje operačný kód a jeho argumenty s dátovými typmi. Toto rozdelenie má na starosti metóda `parse_instruction()`. Po spracovaní a uložení jednotlivých inštrukcií sa zavolá metóda `interpret_code()`, ktorá interpretuje jednotlivé inštrukcie. Na základe operačného kódu inštrukcie volá jemu priradenú metódu. Po úspešnej interpretácii zdrojového kódu sa program ukončí s návratovým kódom 0, čo značí úspech.

Chybové kódy a hlásenia sa nachádzajú v triede `ErrorMessages` v súbore `error.py`. 

Súbor `components.py` obsahuje triedy:
 * `Frames` - slúži na prácu s rámcami
 * `Instruction` - zapúzdruje jednu inštrukciu, ktorá sa skladá z operačného kódu a argumentov, pri každom argumente je uložený aj jeho typ
 * `Variable` - zapúzdruje premennú, čo zahŕňa jej názov, typ, hodnotu a rámec, v ktorom sa aktuálne nachádza. Ďalej umožňuje modifikovať hodnotu a typ premennej.

## test.php ##
 * **jazyk:** PHP 8.1
 * **úloha:** testovanie funkčnosti sktiptov `parse.php` a `interpret.py`

Skript pracuje na základe zadaných argumentov. Akceptovanú sú aj skrátené verzie jednotlivých argumentov. Všetky informácie o podporovaných argumentoch sa zobrazia po vypísaní nápovedy `-h|--help`. Na rekurzívne prehľadávanie priečinkov som využil rozhrania `RecursiveDirectoryIterator` a `RecursiveIteratorIterator` a na následné nájdenie zdrojových súborov regulárne výrazy v spojení s `RegexIterator`.

Na generovanie stránky sa využíva trieda `HTMLGenerator`, ktorá sa nachádza v súbore `src_test/html.generator.php`. Trieda `HTMLGenerator` nepoužíva žiadnu externú knižnicu na generovanie, v triede sa nachádza iba reprezenrácia kódu stránky uložená v niekoľkých premenných, do ktorých sa následne pomocou jednotlivých metód doplnania výsledky testov a nakoniec sa obsah premennej `$pageCode` vypíše na štandardný výstup.

