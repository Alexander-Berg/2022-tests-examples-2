/* syntax version 1 */
$udf = ImagesNN::VisualQualityNetV1(FilePath("nn_vq_v1/upscale_v1_batch.mmap"));

$calc = ($row) -> {

    $result = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc);

    return AsStruct($result.KiwiWormRecord AS KiwiWormRecord, $result.Error AS Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
