/* syntax version 1 */
$keywordsExtract = Prewalrus::KeywordsExtract();

$calc = ($row) -> {
    $keywordsExtractResult = $keywordsExtract(
        $row.TextArc,
        $row.NKeywords,
        $row.OmniNorm,
        $row.Language
    );

    return AsStruct(
        $row.Url AS Url,
        $keywordsExtractResult.Keywords AS Keywords,
        $keywordsExtractResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

