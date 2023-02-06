/* syntax version 1 */
$udf = ImagesNN::SuperResolutionV1(
    FilePath("super_resolution_net_ver1/super_resolution_ver1.cfg"),
    FilePath("super_resolution_net_ver1/super_resolution_ver1.net")
);

$calc = ($row) -> {

    $result = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc);

    return AsStruct($result.KiwiWormRecord AS KiwiWormRecord, $result.Error AS Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

