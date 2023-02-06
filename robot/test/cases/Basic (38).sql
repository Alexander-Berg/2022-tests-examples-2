/* syntax version 1 */
$udf = ImagesPic::ThumbId();

$calc = ($row) -> {
    $result = $udf($row.Thumbnail, $row.GenericImageAttrs);
    return AsStruct($result.Error AS Error, $result.ThumbId AS ThumbId, $result.ThumbIdChunk AS ThumbIdChunk);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

