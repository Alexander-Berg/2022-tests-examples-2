/* syntax version 1 */
$udf = ImagesNN::FacesV3(FilePath("faces_ver3/simfaces_ver3.cfg"),
    FilePath("faces_ver3/facenet_192_ver3.conf"),
    FilePath("faces_ver3/facenet_192_ver3.model"),
    FilePath("faces_ver3/shape_predictor_68_face_landmarks.dat"));

$calc = ($row) -> {
    $result = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc);

    return AsStruct($result.KiwiWormRecord AS KiwiWormRecord, $result.Error AS Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

