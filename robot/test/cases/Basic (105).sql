/* syntax version 1 */
$urlSeg = Prewalrus::UrlSeg();
$dtConv = DtConv::DirectTextDeserializer();

$calc = ($row) -> {
    $directTextResult = $dtConv($row.DirectTextEntries);

    $urlSegResult = $urlSeg(
        $directTextResult.DirectText,
        $row.SegmentatorResult
    );

    return AsStruct(
        $row.Url AS Url,
        $urlSegResult.UrlSegResult AS UrlSegResult,
        $urlSegResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

