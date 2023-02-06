/* syntax version 1 */
$videoThumbsMerge = Video::ThumbsMerge();

$calc = ($row) -> {
    $videoThumbsMergeResult = $videoThumbsMerge(
        $row.Media,
        $row.ThumbMedia
    );

    return AsStruct(
        $row.Url AS Url,
        $videoThumbsMergeResult.Media AS Media,
        $videoThumbsMergeResult.Embed AS Embed,
        $videoThumbsMergeResult.IsWildVideo AS IsWildVideo,
        $videoThumbsMergeResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
