/* syntax version 1 */
$recognizer = Prewalrus::Recognizer(
    FilePath("dict.dict")
);

$calc = ($row) -> {
    $recognizerResult = $recognizer(
        $row.parserChunks,
        $row.baseUrl,
        $row.charset
    );

    return AsStruct(
        $recognizerResult.Charset AS Charset,
        $recognizerResult.Language AS Language,
        $recognizerResult.Language2 AS Language2,
        $recognizerResult.DocLanguages AS DocLanguages,
        $recognizerResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

