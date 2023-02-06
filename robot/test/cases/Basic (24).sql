/* syntax version 1 */
$udf = ImagesNN::FacesV6(FilePath("face_model/facenet_v6_heads.graph"), 0.025f, 0.8f, 5);

$calc = ($row) -> {

    $result = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc, $row.DetectedFaces);
    
    return AsStruct($result.KiwiWormRecord AS KiwiWormRecord, $result.Error AS Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

