/* syntax version 1 */
$udf = ImagesNN::DetectionV3(FilePath("data/clothes_detector_v5.cfg"), FilePath("data/clothes_detector_v5.net"), FilePath("data/clothes_features_v4.pb"));

$calc = ($row) -> {
    $result = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc);

    return AsStruct($result.KiwiWormRecord AS KiwiWormRecord, $result.Error AS Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

