/* syntax version 1 */
$numBuckets = 256;
$fNormalizer = Antispam::FNormalizer(
    FilePath("fnorm.dat"), $numBuckets
);

SELECT
    fNormalizerResult.OutValue,
    fNormalizerResult.Error
FROM (
    SELECT $fNormalizer(InValue) AS fNormalizerResult FROM Input
);
