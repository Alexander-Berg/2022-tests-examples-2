/* syntax version 1 */

$synonym = Prewalrus::Synonym(
    FolderPath("syn_data")
);

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $synonymResult = $synonym(
        $numeratorResult.NumeratorEvents
    );

    return AsStruct(
        $row.Url AS Url,
        $synonymResult.Syn7bV AS Syn7bV,
        $synonymResult.Syn8bV AS Syn8bV,
        $synonymResult.Syn9aV AS Syn9aV,
        $synonymResult.SynPercentBadWordPairs AS SynPercentBadWordPairs,
        $synonymResult.SynNumBadWordPairs AS SynNumBadWordPairs,
        $synonymResult.NumLatinLetters AS NumLatinLetters,
        $synonymResult.Error AS Error 
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

