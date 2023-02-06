/* syntax version 1 */
$portion = Prewalrus::Portion();
$dtConv = DtConv::DirectTextDeserializer();

$calc = ($row) -> {
    $directTextResult = $dtConv($row.DirectTextEntries);

    $portionResult = $portion(
        $directTextResult.DirectText,
        $row.DisambMasks,
        $row.DocAttrs,
        $row.SegmentatorResult,
        $row.AlternateZones,
        $row.DirectTextAttrs,
        $row.FreqCalculatorResult,
        $row.DateExtractorResult,
        $row.NameExtractorResult,
        $row.PhoneNumberResult,
        $row.NumberResult,
        $row.PriceResult,
        $row.ReviewResult,
        $row.ForumResult,
        $row.IndexingSource,
        $row.MergedArcZones,
        $row.NewsHostResult,
        $row.RobotDateResult,
        $row.AlternateHreflangResult,
        $row.TasixHostResult,
        $row.IsProduction
    );

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($portionResult.IndexPortions) AS KeyInvMd5,
        Digest::Md5Hex($portionResult.TextArchivePortion) AS ArcMd5,
        $portionResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

