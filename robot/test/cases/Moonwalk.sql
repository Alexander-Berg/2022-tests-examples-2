/* syntax version 1 */
$videoJsonApi = Video::JsonApi(FolderPath("json_api"));
$mediaToJson = Video::MediaToJson();

$calc = ($row) -> {

    $videoJsonApiResult = $videoJsonApi(
        $row.Url,
        $row.LastAccess,
        $row.`Json`,
        $row.Url
    );

    return AsStruct(
        $row.Url AS Url,
        $videoJsonApiResult.Media AS Media,
        $mediaToJson($videoJsonApiResult.Media).Media AS MediaJson,
        $videoJsonApiResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
