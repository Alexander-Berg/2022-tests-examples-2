/* syntax version 1 */
$udf = Images::KiwiRec2Thumb();

$calc = ($row) -> {
    $result = $udf($row.KiwiRec, $row.ThumbIdChunkId);

    return AsStruct(
        $result.ThumbId AS ThumbId,
        $result.Thumb AS Thumb,
        $result.ImagePropertiesChunk AS ImagePropertiesChunk,
        $result.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
