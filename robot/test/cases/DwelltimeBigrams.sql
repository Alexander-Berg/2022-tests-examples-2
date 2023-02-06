/* syntax version 1 */
$dssmEmbeddingGenerator = Prewalrus::DssmEmbeddingGenerator(
    FolderPath("JUPITER_NEWEST_BASE_DSSM_MODELS"),
    "dwelltime_bigrams_dssm_model.nn_applier",
    "DwelltimeBigrams"
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

