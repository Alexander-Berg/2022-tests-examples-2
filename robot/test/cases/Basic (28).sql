/* syntax version 1 */
$udf = ImagesNN::SuperResolutionV2(
    FilePath("super_resolution_net_ver2/super_resolution_ver2.cfg"),
    FilePath("super_resolution_net_ver2/super_resolution_ver2.net")
);

$calc = ($row) -> {

    $result = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc);

    return AsStruct($result.KiwiWormRecord AS KiwiWormRecord, $result.Error AS Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

