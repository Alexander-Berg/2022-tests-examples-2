/* syntax version 1 */
$dssmEmbeddingGenerator = Prewalrus::DssmEmbeddingGenerator(
    FolderPath("JUPITER_NEWEST_BASE_DSSM_MODELS"),
    "log_dt_bigrams_am_hard_queries_no_clicks_dssm_model.nn_applier",
    "LogDtBigramsAmHardQueriesNoClicks"
);

$calc = ($row) -> {

    $dssmEmbeddingGeneratorResult = $dssmEmbeddingGenerator($row.Url, $row.Title);

    return AsStruct(
        $row.Url AS Url,
        $row.Title AS Title,
        $dssmEmbeddingGeneratorResult.Embedding AS Embedding,
        $dssmEmbeddingGeneratorResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
