/* syntax version 1 */
$sentenceLengths = Prewalrus::SentenceLengths();
$dtConv = DtConv::DirectTextDeserializer();

$calc = ($row) -> {
    $directTextResult = $dtConv($row.DirectTextEntries);

    $sentenceLengthsResult = $sentenceLengths($directTextResult.DirectText);

    return AsStruct(
        $row.Url AS Url,
        $sentenceLengthsResult.SentenceLengths AS SentenceLengths,
        $sentenceLengthsResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

