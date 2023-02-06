/* syntax version 1 */
$videoMediaCanonizer = Video::MediaCanonizer(FolderPath("media_canonizer_config_dir"));

$calc = ($row) -> {

    $videoMediaCanonizerResult = $videoMediaCanonizer($row.Media);

    return AsStruct(
        $row.Url AS Url,
        $videoMediaCanonizerResult.Media AS Media,
        $videoMediaCanonizerResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
