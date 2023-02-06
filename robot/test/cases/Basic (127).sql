/* syntax version 1 */
$videoMetaTextsParser = Video::MetaTextsParser();

$calc = ($row) -> {
    $videoMetaTextsParserResult = $videoMetaTextsParser(
        $row.NumeratorEvents,
        CAST($row.Encoding AS UINT32)
    );

    return AsStruct(
        $row.Url AS Url,
        $videoMetaTextsParserResult.MetaTexts AS MetaTexts,
        $videoMetaTextsParserResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
