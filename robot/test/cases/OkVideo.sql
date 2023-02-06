/* syntax version 1 */
$pluginParser = Video::PluginParser(FolderPath("plugin_parser"));
$mediaToJson = Video::MediaToJson();

$calc = ($row) -> {

    $pluginParserResult = $pluginParser($row.Url, $row.Html);

    return AsStruct(
        $row.Url AS Url,
        $pluginParserResult.Media AS Media,
        $pluginParserResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

SELECT
    Url,
    $mediaToJson($calc(TableRow()).Media) AS Media
FROM
    Input
;
