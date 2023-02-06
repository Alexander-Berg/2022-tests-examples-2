/* syntax version 1 */
$udf = ImagesPic::ParseAvatarsResponse(FilePath("avatars_images_main.conf"));

$calc = ($row) -> {
    $result = $udf($row.AvatarsResponse);

    return AsStruct(
        $result.MdsChunk AS MdsId,
        $result.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
