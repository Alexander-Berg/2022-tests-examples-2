/* syntax version 1 */
$dssmSelectionRankFeatures = Prewalrus::DssmSelectionRankFeatures(
    FolderPath("JUPITER_DSSM_MODELS")
);

$to_str = ($v) -> {
    $s = 1e-5;
    $v2 = cast($v / $s as int64) * $s;
    return cast($v2 as string);
};

$calc = ($row) -> {
    $dssmSelectionRankFeaturesResult = $dssmSelectionRankFeatures(
        $row.Url,
        $row.Title,
        $row.Keywords
    );

    return AsStruct(
        $row.Url AS Url,
        $to_str($dssmSelectionRankFeaturesResult.HaveShowsUrlTitleKeywordsPrediction) AS HaveShowsUrlTitleKeywordsPrediction,
        $to_str($dssmSelectionRankFeaturesResult.HaveClicksUrlTitleKeywordsPrediction) AS HaveClicksUrlTitleKeywordsPrediction,
        $to_str($dssmSelectionRankFeaturesResult.LogClicksUrlTitleKeywordsPrediction) AS LogClicksUrlTitleKeywordsPrediction,
        $dssmSelectionRankFeaturesResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

