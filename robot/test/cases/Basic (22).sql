/* syntax version 1 */
$udf = ImagesNN::FacesV4(FilePath("face_model/simfaces_ver4fast_trigger.cfg"),
    FilePath("face_model/facenet_ver4fast.conf"),
    FilePath("face_model/facenet_ver4fast.model"),
    FilePath("face_model/shape_predictor_68_face_landmarks.dat"));

$calc = ($row) -> {

    $result = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc);
    
    return AsStruct($result.KiwiWormRecord AS KiwiWormRecord, $result.Error AS Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

