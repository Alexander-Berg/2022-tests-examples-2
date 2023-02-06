/* syntax version 1 */
$udf = ImagesNN::DetectionV1(FilePath("detector_v1_configs/clothes_detector_v3.cfg"), FilePath("detector_v1_configs/clothes_detector_v3.net"), FilePath("detector_v1_configs/clothes_features_extractor.cfg"), FilePath("detector_v1_configs/clothes_features_extractor.net"));

$calc = ($row) -> {
    $result = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc);

    return AsStruct($result.KiwiWormRecord AS KiwiWormRecord, $result.Error AS Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

