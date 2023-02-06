/* syntax version 1 */
$videoUrlInfo = Video::UrlInfo(FolderPath("video_url_info_configs"));

$calc = ($row) -> {
    $videoUrlInfoResult = $videoUrlInfo($row.Media, $row.IsNews);

    return AsStruct(
        $row.Url AS Url,
        $videoUrlInfoResult.Media AS Media,
        $videoUrlInfoResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
