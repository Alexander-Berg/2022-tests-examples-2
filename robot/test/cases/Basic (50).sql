/* syntax version 1 */
$dssmEmbedding = Prewalrus::DssmEmbedding(
    FolderPath("JUPITER_DSSM_MODELS")
);

$calc = ($row) -> {
    $dssmEmbeddingResult = $dssmEmbedding(
        $row.Url,
        $row.Title
    );

    return AsStruct(
        $row.Url AS Url,
        $dssmEmbeddingResult.Embedding AS Embedding,
        $dssmEmbeddingResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

