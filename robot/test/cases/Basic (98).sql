/* syntax version 1 */
$textArcReader = Prewalrus::TextArcReader();

$calc = ($row) -> {
    $textArcReaderResult = $textArcReader(
        $row.TextArc,
        $row.PlainText,
        $row.RawYandex,
        $row.ZoneNum
    );

    return AsStruct(
        $row.Url AS Url,
        $textArcReaderResult.Text AS Text,
        $textArcReaderResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

