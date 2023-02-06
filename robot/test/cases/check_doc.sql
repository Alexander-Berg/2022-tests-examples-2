
-- TODO: Replace `$row.HttpBody` with a `$row.Html` in script and tests data

SELECT
    NewsProcessing::CheckDoc(NewsProcessing::RawNewsDocExtractor(ZoraCtx),
    if (CanBeParsed, HttpBody, NULL), CAST(1.0 AS float), Charset)
FROM Input
;
