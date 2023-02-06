/* syntax version 1 */
$videoMediaMarkRotor = Video::MediaMarkRotor();

SELECT
    Url,
    $videoMediaMarkRotor(Media).Media AS Media
FROM
    Input
;
