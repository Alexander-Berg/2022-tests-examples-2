/* syntax version 1 */
$simpleSimhash = Prewalrus::SimpleSimhash(FolderPath("pure"));

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $simpleSimhashResult = $simpleSimhash($numeratorResult.NumeratorEvents, $row.ZoneData, $row.Language, $row.Language2);

    return AsStruct(
        $row.Url AS Url,
        $simpleSimhashResult.Simhash AS Simhash,
        $simpleSimhashResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

