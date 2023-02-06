$GetRawNewsDoc = NewsProcessing::RawNewsDocExtractor;
$CheckDoc = NewsProcessing::CheckDoc;
$FetchLinks = NewsProcessing::FetchLinks;

$Recognizer = FilePath("link-fetcher-recognizer.dict");
$Htparserini = FilePath("htparser.ini");
$Xpathrules = FilePath("xpath_rules.json");


$extractUkropCtx = Common::ExtractUkropCtx();

$ExtractUkropCtx = ($ZoraCtx) -> {
    return IF($ZoraCtx IS NOT NULL, $extractUkropCtx($ZoraCtx));
};

$env = Common::GetEnv("YQL_CONFIG_NAME");
$testTimestamp = Common::GetEnv("TEST_TIMESTAMP");
$now = ($dependson) -> {
  return IF($env != "testing", YQL::Now($dependson), CAST($testTimestamp As Uint64) ?? 0);
};

-- TODO: Replace `$row.HttpBody` with a `$row.Html` in script and tests data

$FetchExternalLinks = ($row) -> {
    $Doc = $GetRawNewsDoc($row.ZoraCtx);
    $DoFetchLinks = $FetchLinks($Doc, $row.HttpBody, $row.MimeType, $row.Charset, $Recognizer, $Htparserini, $Xpathrules);
    $IsFetchSafe = $row.CanBeParsed;
    return if ($IsFetchSafe, $DoFetchLinks, NULL);
};

$DocWithStatus = ($HttpBody, $Doc, $CanBeParsed, $Charset) -> {
    return $CheckDoc($Doc, if ($CanBeParsed, $HttpBody, NULL), CAST(1.0 AS float), $Charset);
};

$ComposeNewsDoc = ($row) -> {
    $LastAccess = if ($row.LastAccess == 0, $now(YQL::DependsOn($row)) / 1000000ul, $row.LastAccess);
    $PatchedLastAccess = Yql::Unwrap(CAST($LastAccess AS Uint32));
    $UkropCtx = $ExtractUkropCtx($row.ZoraCtx);
    $Doc = $GetRawNewsDoc($row.ZoraCtx);
    $ExportDoc = NewsProcessing::ComposeDoc();
    return $ExportDoc($DocWithStatus($row.HttpBody, $Doc, $row.CanBeParsed, $row.Charset),
                      $PatchedLastAccess,
                      $FetchExternalLinks($row),
                      $UkropCtx.NEWS_PAGES_NEW IS NOT NULL,
                      $row.HttpCode);
};

SELECT
    $ComposeNewsDoc(TableRow())
From Input
;
