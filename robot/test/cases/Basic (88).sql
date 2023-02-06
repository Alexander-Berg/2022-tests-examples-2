/* syntax version 1 */
$segmentTrigram = Prewalrus::SegmentTrigram();
$dtConv = DtConv::DirectTextDeserializer();

$calc = ($row) -> {
    $directTextResult = $dtConv($row.DirectTextEntries);

    $segmentTrigramResult = $segmentTrigram(
        $directTextResult.DirectText,
        $row.SegmentatorResult
    );

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($segmentTrigramResult.FooterTrigrams) AS FooterTrigramsMd5,
        $segmentTrigramResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

