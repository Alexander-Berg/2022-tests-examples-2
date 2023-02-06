/* syntax version 1 */
$dssmOptimizedRthubModel = Prewalrus::DssmOptimizedRthubModel();

$calc = ($row) -> {
    $dssmOptimizedRthubModelResult = $dssmOptimizedRthubModel($row.Keywords, $row.Url, $row.Title, $row.UltimateDescription);

    $dssmMainContentKeywordsResult =
        Prewalrus::DssmOptimizedRthubModelExtractEmbedding(
            $dssmOptimizedRthubModelResult.Result,
            "doc_embedding_main_content_keywords_document",
            "MainContentKeywords",
            "20180524");

    $dssmEmbeddingResult =
        Prewalrus::DssmOptimizedRthubModelExtractEmbedding(
            $dssmOptimizedRthubModelResult.Result,
            "doc_embedding_bigrams_l2",
            "LogDwellTimeBigrams",
            "0");

    $selectionRankFeaturesHaveClicksResult =
        Prewalrus::DssmOptimizedRthubModelExtractPredict(
            $dssmOptimizedRthubModelResult.Result,
            "joint_output_selection_rank_features_have_clicks",
            "20180524");

    $selectionRankFeaturesHaveShowsResult =
        Prewalrus::DssmOptimizedRthubModelExtractPredict(
            $dssmOptimizedRthubModelResult.Result,
            "joint_output_selection_rank_features_have_shows",
            "20180524");

    $selectionRankFeaturesLogClicksResult =
        Prewalrus::DssmOptimizedRthubModelExtractPredict(
            $dssmOptimizedRthubModelResult.Result,
            "joint_output_selection_rank_features_log_clicks",
            "20180524");

    $dwelltimeBigramsResult =
        Prewalrus::DssmOptimizedRthubModelExtractEmbedding(
            $dssmOptimizedRthubModelResult.Result,
            "doc_embedding_dwelltime_bigrams",
            "DwelltimeBigrams",
            "0");

    $dwelltimeMulticlickResult =
        Prewalrus::DssmOptimizedRthubModelExtractEmbedding(
            $dssmOptimizedRthubModelResult.Result,
            "doc_embedding_dwelltime_multiclick",
            "DwelltimeMulticlick",
            "0");

    $fpsSpylogAggregatedResult =
        Prewalrus::DssmOptimizedRthubModelExtractEmbedding(
            $dssmOptimizedRthubModelResult.Result,
            "doc_embedding_fps_spylog_aggregated_doc_part",
            "FpsSpylogAggregatedDocPart",
            "0");

    $userHistoryHostClusterResult =
        Prewalrus::DssmOptimizedRthubModelExtractEmbedding(
            $dssmOptimizedRthubModelResult.Result,
            "doc_embedding_user_history_host_cluster_doc_part",
            "UserHistoryHostClusterDocPart",
            "0");

    $logDtBigramsAmHardQueriesNoClicksResult =
        Prewalrus::DssmOptimizedRthubModelExtractEmbedding(
            $dssmOptimizedRthubModelResult.Result,
            "doc_embedding_log_dt_bigrams_am_hard_queries_no_clicks",
            "LogDtBigramsAmHardQueriesNoClicks",
            "1");

    $logDtBigramsAmHardQueriesNoClicksMixedResult =
        Prewalrus::DssmOptimizedRthubModelExtractEmbedding(
            $dssmOptimizedRthubModelResult.Result,
            "doc_embedding_log_dt_bigrams_am_hard_queries_no_clicks_mixed",
            "LogDtBigramsAmHardQueriesNoClicksMixed",
            "1");

    $dssmBertDistillL2Result =
        Prewalrus::DssmOptimizedRthubModelExtractEmbedding(
            $dssmOptimizedRthubModelResult.Result,
            "doc_embedding_dssm_bert_distill_l2",
            "LogDwellTimeBigrams",
            "1");

    $serializedProtoOfOptimizedRthubModelApply =
        Prewalrus::DssmOptimizedRthubModelSerializeToProto(
            $dssmOptimizedRthubModelResult.Result);

    return AsStruct(
        $row.Url AS Url,
        $dssmOptimizedRthubModelResult.Error AS Error,

        $serializedProtoOfOptimizedRthubModelApply.Result AS serializedProtoOfOptimizedRthubModelApplyResult,
        $serializedProtoOfOptimizedRthubModelApply.Error AS serializedProtoOfOptimizedRthubModelApplyError,

        $dssmMainContentKeywordsResult.Error AS ExtractErrorOfMainContentKeywordsDocument,
        $dssmMainContentKeywordsResult.Embedding AS EmbeddingOfMainContentKeywordsDocument,
        $dssmMainContentKeywordsResult.Version AS VersionOfMainContentKeywordsDocument,

        $dssmEmbeddingResult.Error AS ExtractErrorOfDssmEmbedding,
        $dssmEmbeddingResult.Embedding AS EmbeddingOfDssmEmbedding,
        $dssmEmbeddingResult.Version AS VersionOfDssmEmbedding,

        Math::Round($selectionRankFeaturesHaveShowsResult.Predict, -5) AS PredictOfHaveShowsUrlTitleKeywords,
        $selectionRankFeaturesHaveShowsResult.Error AS ExtractErrorOfHaveShowsUrlTitleKeywords,

        Math::Round($selectionRankFeaturesHaveClicksResult.Predict, -5) AS PredictOfHaveClicksUrlTitleKeywords,
        $selectionRankFeaturesHaveClicksResult.Error AS ExtractErrorOfHaveClicksUrlTitleKeywords,

        Math::Round($selectionRankFeaturesLogClicksResult.Predict, -5) AS PredictOfLogClicksUrlTitleKeywords,
        $selectionRankFeaturesLogClicksResult.Error AS ExtractErrorOfLogClicksUrlTitleKeywords,

        $dwelltimeBigramsResult.Error AS ExtractErrorOfDwelltimeBigrams,
        $dwelltimeBigramsResult.Embedding AS EmbeddingOfDwelltimeBigrams,
        $dwelltimeBigramsResult.Version AS VersionOfDwelltimeBigrams,

        $dwelltimeMulticlickResult.Error AS ExtractErrorOfDwelltimeMulticlick,
        $dwelltimeMulticlickResult.Embedding AS EmbeddingOfDwelltimeMulticlick,
        $dwelltimeMulticlickResult.Version AS VersionOfDwelltimeMulticlick,

        $fpsSpylogAggregatedResult.Error AS ExtractErrorOfFpsSpylogAggregated,
        $fpsSpylogAggregatedResult.Embedding AS EmbeddingOfFpsSpylogAggregated,
        $fpsSpylogAggregatedResult.Version AS VersionOfFpsSpylogAggregated,

        $userHistoryHostClusterResult.Error AS ExtractErrorOfUserHistoryHostCluster,
        $userHistoryHostClusterResult.Embedding AS EmbeddingOfUserHistoryHostCluster,
        $userHistoryHostClusterResult.Version AS VersionOfUserHistoryHostCluster,

        $logDtBigramsAmHardQueriesNoClicksResult.Error AS ExtractErrorOfLogDtBigramsAmHardQueriesNoClicks,
        $logDtBigramsAmHardQueriesNoClicksResult.Embedding AS EmbeddingOfLogDtBigramsAmHardQueriesNoClicks,
        $logDtBigramsAmHardQueriesNoClicksResult.Version AS VersionOfLogDtBigramsAmHardQueriesNoClicks,

        $logDtBigramsAmHardQueriesNoClicksMixedResult.Error AS ExtractErrorOfLogDtBigramsAmHardQueriesNoClicksMixed,
        $logDtBigramsAmHardQueriesNoClicksMixedResult.Embedding AS EmbeddingOfLogDtBigramsAmHardQueriesNoClicksMixed,
        $logDtBigramsAmHardQueriesNoClicksMixedResult.Version AS VersionOfLogDtBigramsAmHardQueriesNoClicksMixed,

        $dssmBertDistillL2Result.Error AS ExtractErrorOfDssmBertDistillL2Result,
        $dssmBertDistillL2Result.Embedding AS EmbeddingOfDssmBertDistillL2Result,
        $dssmBertDistillL2Result.Version AS VersionOfDssmBertDistillL2Result,
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

