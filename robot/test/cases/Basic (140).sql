/* syntax version 1 */
$videoWebAttrsSetter = Video::WebAttrsSetter();

$calc = ($row) -> {
    $videoWebAttrsSetterResult = $videoWebAttrsSetter(
        $row.Media,
        $row.Title
    );

    return AsStruct(
        $row.Url AS Url,
        $videoWebAttrsSetterResult.Media AS Media,
        $videoWebAttrsSetterResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
