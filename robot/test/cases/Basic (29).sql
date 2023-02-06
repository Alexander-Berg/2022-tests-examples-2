/* syntax version 1 */
$udf = ImagesNN::SuperResolutionV3(
    FilePath("super_resolution_net_ver3/super_resolution_ver3.cfg"),
    FilePath("super_resolution_net_ver3/super_resolution_ver3.net"),
    FilePath("super_resolution_net_ver3/shape_predictor_68_face_landmarks.dat")
);

$calc = ($row) -> {

    $result = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc);

    return AsStruct($result.KiwiWormRecord AS KiwiWormRecord, $result.Error AS Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
