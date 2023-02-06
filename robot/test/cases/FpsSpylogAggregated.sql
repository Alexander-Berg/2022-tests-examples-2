/* syntax version 1 */
$dssmEmbeddingGenerator = Prewalrus::DssmEmbeddingGenerator(
    FolderPath("JUPITER_NEWEST_BASE_DSSM_MODELS"),
    "fps_spylog_aggregated_doc_part_dssm_model.nn_applier",
    "FpsSpylogAggregatedDocPart"
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

