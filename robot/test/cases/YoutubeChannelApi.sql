/* syntax version 1 */
$authorJsonApi = Video::AuthorJsonApi(FolderPath("author_json_api"));

$calc = ($row) -> {

    $authorJsonApiResult = $authorJsonApi($row.Url, NULL, $row.`Json`);

    return AsStruct(
        $row.Url AS Url,
        $authorJsonApiResult.Author AS Author,
        $authorJsonApiResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

SELECT
    Url,
    Video::AuthorToJson($calc(TableRow()).Author) AS Author
FROM
    Input
;
