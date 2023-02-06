/* syntax version 1 */
$videoMediaMerge = Video::MediaMerge();

$calc = ($row) -> {
    $videoMediaMergeResult = $videoMediaMerge(
        $row.LhsMedia,
        $row.RhsMedia
    );

    return AsStruct(
        $videoMediaMergeResult.Media AS Media,
        $videoMediaMergeResult.Error AS Error
    );
};

SELECT * FROM
   (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
