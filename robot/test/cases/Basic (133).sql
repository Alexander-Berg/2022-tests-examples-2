/* syntax version 1 */
$videoSourceCombine = Video::SourceCombine(FilePath("config.json"));

$calc = ($row) -> {

    $videoSourceCombineResult = $videoSourceCombine(
        $row.Media,
        $row.Url,
        $row.Encoding
    );

    return AsStruct(
        $row.Url AS Url,
        $videoSourceCombineResult.Media AS Media,
        $videoSourceCombineResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
