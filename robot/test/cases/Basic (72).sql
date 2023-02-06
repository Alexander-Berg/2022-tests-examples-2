/* syntax version 1 */
$nameExtractor = Prewalrus::NameExtractor(
    FolderPath("fio")
);

$calc = ($row) -> {
    $dtConv = DtConv::DirectTextDeserializer();
    $directTextResult = $dtConv($row.DirectTextEntries);

    $nameExtractorResult = $nameExtractor($directTextResult.DirectText);

    return AsStruct(
        $row.Url AS Url,
        $nameExtractorResult.NameExtractorResult AS NameExtractorResult,
        $nameExtractorResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

