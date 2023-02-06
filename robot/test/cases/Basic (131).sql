/* syntax version 1 */
$videoSeries = Video::Series(FolderPath("video_series_configs"));

$calc = ($row) -> {

    $videoSeriesResult = $videoSeries($row.Media);

    return AsStruct(
        $row.Url AS Url,
        $videoSeriesResult.Media AS Media,
        $videoSeriesResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
