/* syntax version 1 */
$pluginParser = Video::PluginParser(FolderPath("plugin_parser"));

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
