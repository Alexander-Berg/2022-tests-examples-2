/* syntax version 1 */
$number = Prewalrus::Number(
    FolderPath("numbers"),
);

$calc = ($row) -> {
    $dtConv = DtConv::DirectTextDeserializer();
    $directTextResult = $dtConv($row.DirectTextEntries);

    $numberResult = $number($directTextResult.DirectText);

    return AsStruct(
        $row.Url AS Url,
        $numberResult.NumberResult AS NumberResult,
        $numberResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

