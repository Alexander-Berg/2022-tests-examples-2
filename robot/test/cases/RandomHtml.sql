/* syntax version 1 */
$xpathParser = Video::XpathParser(FolderPath("xpath_parser"));
$authorJsonApi = Video::AuthorJsonApi(FolderPath("author_json_api"));

$calc = ($row) -> {

    $xpathParserResult = $xpathParser($row.Url, $row.Html);
    $authorJsonApiResult = $authorJsonApi($row.Url, "xpath.video.yandex.ru", $xpathParserResult.`Json`);

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
