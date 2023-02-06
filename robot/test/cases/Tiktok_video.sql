/* syntax version 1 */

$watsonVideoParsersImpl = AsList(
    AsStruct(
        'youtube' AS Id,
        'youtube.com' AS Host,
        @@^https://www\.youtube\.com/watch\?v=@@ AS RegEx,
        FilePath('watson_youtube.json') AS ConfigFile
    ),
    AsStruct(
        'pornhub' AS Id,
        'pornhub.com' AS Host,
        @@^https://\w+\.pornhub\.com/view_video\.php\?.*viewkey=@@ AS RegEx,
        FilePath('watson_pornhub.json') AS ConfigFile
    ),
    AsStruct(
        'xvideos' AS Id,
        'www.xvideos.com' AS Host,
        @@^https://www\.xvideos\.com/video@@ AS RegEx,
        FilePath('watson_xvideos.json') AS ConfigFile
    ),
    AsStruct(
        'watson.tiktok_video.com' AS Id,
        'www.tiktok.com' AS Host,
        @@^https://www\.tiktok\.com/@[^/]+/video/\d+@@ AS RegEx,
        FilePath('watson_tiktok_video.json') AS ConfigFile
    ),
    AsStruct(
        'watson.ok.ru' AS Id,
        'ok.ru' AS Host,
        @@^https://ok\.ru/video/@@ AS RegEx,
        FilePath('watson_ok.json') AS ConfigFile
    ),
);
$watsonVideoParsers = Watson::FromParserList($watsonVideoParsersImpl);
$videoJsonApi = Video::JsonApi(FolderPath("json_api"));

$WatsonParse = ($html, $url, $charset, $indexDate) -> {
    $parserResult = $watsonVideoParsers($html, $url, $charset);
    $data = IF(ListLength($parserResult) != 0, $parserResult[0]);
    $result = IF($data.Id in ("watson.tiktok_video.com"), Cast(Yson::ConvertToString($data.Result[0].data) As Json), Yson::SerializeJson($data.Result));

    return IF($data is not null, $videoJsonApi($url, CAST($indexDate AS Uint32), CAST($result as String), $url));
};

$mediaToJson = Video::MediaToJson();
$parse = ($row) -> {
    $watsonParserResult = $WatsonParse($row.Html, $row.Url, $row.Charset, 1644800000);

    return AsStruct(
        $row.Url AS Url,
        $watsonParserResult.Media AS Media,
        $mediaToJson($watsonParserResult.Media) AS Json,
        $watsonParserResult.Error AS Error);
};

SELECT * FROM
(SELECT $parse(TableRow()) FROM Input)
FLATTEN COLUMNS;
