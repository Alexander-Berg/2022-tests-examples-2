/* syntax version 1 */
$titleBreaks = Prewalrus::TitleBreaks();
$dtConv = DtConv::DirectTextDeserializer();

$calc = ($row) -> {
    $directTextResult = $dtConv($row.DirectTextEntries);

    $titleBreaksResult = $titleBreaks($directTextResult.DirectText);

    return AsStruct(
        $row.Url AS Url,
        $titleBreaksResult.TitleFirstBreak AS TitleFirstBreak,
        $titleBreaksResult.TitleLastBreak AS TitleLastBreak,
        $titleBreaksResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

