/* syntax version 1 */
$udf = ImagesNN::DetectionV4(FilePath("data/clothes_detector_with_gender_adult.cfg"), FilePath("data/clothes_detector_with_gender_adult.net"), FilePath("data/clothes_features_v5.pb"));

$calc = ($row) -> {
    $result = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc);

    return AsStruct($result.KiwiWormRecord AS KiwiWormRecord, $result.Error AS Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

