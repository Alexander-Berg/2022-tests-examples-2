/* syntax version 1 */
$dssmEmbeddingGenerator = Prewalrus::DssmEmbeddingGenerator(
    FolderPath("JUPITER_NEWEST_BASE_DSSM_MODELS"),
    "user_history_host_cluster_doc_part_dssm_model.nn_applier",
    "UserHistoryHostClusterDocPart"
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

