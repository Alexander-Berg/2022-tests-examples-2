$Recognizer = FilePath("link-fetcher-recognizer.dict");
$Htparserini = FilePath("htparser.ini");
$Xpathrules = FilePath("xpath_rules.json");

$GetRawNewsDoc = NewsProcessing::RawNewsDocExtractor;
$CheckDoc = NewsProcessing::CheckDoc;
$FetchLinks = NewsProcessing::FetchLinks;

$FetchExternalLinks = ($row) -> {
    $Doc = $GetRawNewsDoc($row.ZoraCtx);
    $DoFetchLinks = $FetchLinks($Doc, $row.HttpBody, $row.MimeType, $row.Charset, $Recognizer, $Htparserini, $Xpathrules);
    $IsFetchSafe = $row.CanBeParsed;
    return if ($IsFetchSafe, $DoFetchLinks, NULL);
};

$links = $FetchExternalLinks(TableRow());

SELECT
    NewsProcessing::ExportLinksToSamovar(YQL::Unwrap($links))
FROM Input
;