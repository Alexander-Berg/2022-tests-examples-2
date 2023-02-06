$Recognizer = FilePath("link-fetcher-recognizer.dict");
$Htparserini = FilePath("htparser.ini");
$Xpathrules = FilePath("xpath_rules.json");

SELECT
    CAST(NewsProcessing::Snippet(Unwrap(HttpBody), Unwrap(MimeType), Charset ?? -1, $Recognizer, $Htparserini, $Xpathrules) AS Utf8) ?? "" AS Snippet
FROM Input
;

