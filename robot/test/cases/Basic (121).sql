/* syntax version 1 */
$videoMediaFilter = Video::MediaFilter();

SELECT
    Url,
    $videoMediaFilter(Media, 4, "").Media AS Media,
    $videoMediaFilter(Media, 3, "").Media AS Embed
FROM
    Input
;
