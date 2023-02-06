/* syntax version 1 */
$videoMediaTextRecognizer = Video::MediaTextRecognizer(FilePath("dict.dict"));

$calc = ($row) -> {
    $videoMediaTextRecognizerResult = $videoMediaTextRecognizer(
        $row.Media,
        $row.Url,
        CAST($row.Language AS UINT8)
    );

    return AsStruct(
        $videoMediaTextRecognizerResult.Media AS Media,
        $videoMediaTextRecognizerResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
