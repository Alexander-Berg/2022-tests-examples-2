/* syntax version 1 */
$udf = ImagesPic::ThumbnailInfo();

$calc = ($row) -> {
    $result = $udf($row.Thumbnail, $row.GenericImageAttrs);
    return AsStruct($result.Error AS Error, $result.ThumbnailInfo AS ThumbnailInfo);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

