/* syntax version 1 */
$parsers = AsList(
    AsStruct(
        'watson.tiktok.com' AS Id,
        'www.tiktok.com' AS Host,
        @@^https://www\.tiktok\.com/@[^/]+$@@ AS RegEx,
        FilePath('watson_parsers/watson_tiktok_channel.json') AS ConfigFile
    ),
    AsStruct(
        'watson.instagram.com' AS Id,
        'www.instagram.com' AS Host,
        @@^https://www\.instagram\.com/[^/]+/$@@ AS RegEx,
        FilePath('watson_parsers/watson_instagram_channel.json') AS ConfigFile
    ),
);
$parser = Watson::FromParserList($parsers);
$authorJsonApi = Video::AuthorJsonApi(FolderPath("author_json_api"));

$calc = ($row) -> {
    $parserResult = $parser($row.Html, $row.Url, $row.Charset);
    $data = ListFilter($parserResult, ($x)-> {return not Yson::IsEntity($x.Result[0].data);});
    $data = IF(ListLength($data) != 0, $data[0]);
    $authorJsonApiResult = IF($data is not Null, $authorJsonApi($row.Url, $data.Id, Yson::ConvertToString($data.Result[0].data)));

    return AsStruct(
        $row.Url AS Url,
        $authorJsonApiResult.Author as Author,
        $authorJsonApiResult.Error as Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
