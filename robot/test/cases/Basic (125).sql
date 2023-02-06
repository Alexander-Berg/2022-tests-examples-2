/* syntax version 1 */
$videoMediaToJson = Video::MediaToJson();

$calc = ($row) -> {

    $videoMediaToJsonResult = $videoMediaToJson($row.Media);

    return AsStruct(
        $row.Url AS Url,
        $videoMediaToJsonResult.Media AS Media,
        $videoMediaToJsonResult.Error AS Error
    );   
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
