/* syntax version 1 */
$videoEmbedDetector = Video::EmbedDetector(
    FolderPath("media_canonizer_config_dir"), FilePath("host_whitelist"));

$videoToJson = Video::MediaToJson();

$calc = ($row) -> {
    $embedDetectorResult = $videoEmbedDetector($row.Media);
    $toJson = $videoToJson($row.Media);
    return AsStruct(
        $row.Url AS Url,
        $embedDetectorResult.IsEmbed AS IsEmbed,
        $embedDetectorResult.Error AS Error,
        $toJson.Media as Media
    );
};

SELECT * FROM (
    SELECT $calc(TableRow()) FROM Input
) FLATTEN COLUMNS;
