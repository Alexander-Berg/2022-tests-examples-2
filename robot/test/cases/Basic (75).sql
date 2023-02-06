/* syntax version 1 */
$numerator = Prewalrus::Numerator(
    FolderPath("numerator_config")
);

$calc = ($row) -> {
    $numeratorResult = $numerator(
        $row.ParserChunks,
        $row.Charset,
        $row.Language,
        $row.Url,
        $row.CompatibilityMode,
        $row.OutputZoneIndex,
        $row.IndexAttributes
    );

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($numeratorResult.NumeratorEventsString) AS NumeratorEventsMd5,
        Digest::Md5Hex($numeratorResult.ZoneBlogData) AS ZoneBlogDataMd5,
        Digest::Md5Hex($numeratorResult.ZoneData) AS ZoneDataMd5,
        Digest::Md5Hex($numeratorResult.ZoneImgData) AS ZoneImgDataMd5,
        Digest::Md5Hex($numeratorResult.ZoneVideoData) AS ZoneVideoDataMd5,
        $numeratorResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

