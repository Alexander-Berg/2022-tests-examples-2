/* syntax version 1 */
$udf = ImagesNN::NeuralNetV5(FilePath("nn_v5_config/multihead_net_ver5.cfg"), FilePath("nn_v5_config/multihead_net_ver5.net"));

$calc = ($row) -> {

    $result = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc);

    return AsStruct($result.KiwiWormRecord AS KiwiWormRecord, $result.Error AS Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

