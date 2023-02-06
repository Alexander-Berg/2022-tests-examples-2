/* syntax version 1 */
$titleFeature = Prewalrus::TitleFeature(
    FolderPath("pure")
);
$dtConv = DtConv::DirectTextDeserializer();

$calc = ($row) -> {
    $directTextResult = $dtConv($row.DirectTextEntries);

    $titleFeatureResult = $titleFeature($directTextResult.DirectText);

    return AsStruct(
        $row.Url AS Url,
        $titleFeatureResult.TitleBM25Ex AS TitleBM25Ex,
        $titleFeatureResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

