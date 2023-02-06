/* syntax version 1 */
$extractUkropCtx = Common::ExtractUkropCtx(
);

$calc = ($row) -> {
    $extractUkropCtxResult = $extractUkropCtx(
        $row.ZoraCtx
    );

    return AsStruct(
        $row.Url AS Url,
        $extractUkropCtxResult.Flags AS Flags,
        $extractUkropCtxResult.CrawlAddTime AS CrawlAddTime,
        $extractUkropCtxResult.CrawlTimestamp AS CrawlTimestamp,
        $extractUkropCtxResult.CrawlTimestampFrom AS CrawlTimestampFrom,
        $extractUkropCtxResult.Error AS Error,
        ($extractUkropCtxResult.WEB IS NOT NULL) AS IsWeb,
        ($extractUkropCtxResult.IMAGE IS NOT NULL) AS IsImage,
        ($extractUkropCtxResult.VIDEO IS NOT NULL) AS IsVideo,
        False AS IsTurbo,
        ($extractUkropCtxResult.SPRAV IS NOT NULL) AS IsSprav,
        $extractUkropCtxResult.CampaignType ?? "" AS CampaignType
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
