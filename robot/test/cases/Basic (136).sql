/* syntax version 1 */
$videoUltraFormer = Video::UltraFormer(
    FilePath("ultra-sources.cfg")
);

$calc = ($row) -> {
    $videoUltraFormerResult = $videoUltraFormer(
        $row.Url,
        $row.Media,
        $row.`Date`
    );

    return AsStruct(
        $videoUltraFormerResult.IsValidForUltra AS IsValidForUltra,
        $videoUltraFormerResult.Media AS Media,
        $videoUltraFormerResult.IsNews AS IsNews,
        $videoUltraFormerResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

