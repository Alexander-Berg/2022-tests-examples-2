/* syntax version 1 */
$dssmMainContentKeywords = Prewalrus::DssmMainContentKeywords(
    FolderPath("JUPITER_DSSM_MODELS")
);

$calc = ($row) -> {
    $dssmMainContentKeywordsResult = $dssmMainContentKeywords($row.Keywords);

    return AsStruct(
        $row.Url AS Url,
        $dssmMainContentKeywordsResult.Embedding AS Embedding,
        $dssmMainContentKeywordsResult.Error AS Error
    );
};

SELECT * FROM
   (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

