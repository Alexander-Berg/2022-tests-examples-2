/* syntax version 1 */
$dateExtractor = Prewalrus::DateExtractor();

$calc = ($row) -> {
    $dtConv = DtConv::DirectTextDeserializer();
    $directTextResult = $dtConv($row.DirectTextEntries);

    $dateExtractorResult = $dateExtractor($directTextResult.DirectText, $row.SegmentatorResult);

    return AsStruct(
        $row.Url AS Url,
        $dateExtractorResult.DaterDate AS DaterDate,
        $dateExtractorResult.TopDates AS TopDates,
        $dateExtractorResult.DaterStats AS DaterStats,
        $dateExtractorResult.DaterStatsDM AS DaterStatsDM,
        $dateExtractorResult.DaterStatsMY AS DaterStatsMY,
        Digest::Md5Hex($dateExtractorResult.DateExtractorResult) AS DateExtractorResultMd5,
        $dateExtractorResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

