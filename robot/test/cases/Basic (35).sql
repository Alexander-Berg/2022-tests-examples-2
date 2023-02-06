/* syntax version 1 */
$udf = ImagesPic::Bars();

$calc = ($row) -> {
    $result = $udf($row.Thumbnail);

    return AsStruct($result.Error AS Error, $result.Bars AS Bars);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

