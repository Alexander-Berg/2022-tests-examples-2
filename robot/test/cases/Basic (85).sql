/* syntax version 1 */
$review = Prewalrus::Review();
$dtConv = DtConv::DirectTextDeserializer();

$calc = ($row) -> {
    $directTextResult = $dtConv($row.DirectTextEntries);

    $reviewResult = $review(
        $directTextResult.DirectText,
        $row.SegmentatorResult
    );

    return AsStruct(
        $row.Url AS Url,
        $reviewResult.HasUserReviewsL AS HasUserReviewsL,
        $reviewResult.HasUserReviewsH AS HasUserReviewsH,
        $reviewResult.NumXPathUserReviews AS NumXPathUserReviews,
        $reviewResult.LastXPathUserReviewDate AS LastXPathUserReviewDate,
        $reviewResult.AverageXPathUserReviewRate AS AverageXPathUserReviewRate,
        $reviewResult.MaxXPathUserReviewUsefulness AS MaxXPathUserReviewUsefulness,
        $reviewResult.ReviewResult AS ReviewResult,
        $reviewResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

