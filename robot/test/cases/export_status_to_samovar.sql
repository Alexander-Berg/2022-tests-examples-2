$CheckDoc = NewsProcessing::CheckDoc;

$RawNewsDoc = ($row) -> { RETURN NewsProcessing::RawNewsDocExtractor($row.ZoraCtx); };

$DocWithStatus = ($HttpBody, $Doc, $CanBeParsed, $Charset) -> {
    return $CheckDoc($Doc, if ($CanBeParsed, $HttpBody, NULL), CAST(1.0 AS float), $Charset);
};

$IsNormalDoc = ($row) -> {
    RETURN $DocWithStatus($row.HttpBody, $RawNewsDoc($row), $row.CanBeParsed, $row.Charset).Status == 0;
};

SELECT
    NewsProcessing::ExportStatusToSamovar($RawNewsDoc(TableRow()).Url, "news-url-recrawl-dead", $IsNormalDoc(TableRow()))
FROM Input
;