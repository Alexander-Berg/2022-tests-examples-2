/* syntax version 1 */
$numerator = Prewalrus::Numerator(
    FolderPath("numerator_config")
);

$calc = ($row) -> {
    $numeratorResult = $numerator(
        $row.ParserChunks,
        $row.Charset,
        $row.Language,
        $row.Url,
        $row.CompatibilityMode,
        $row.OutputZoneIndex,
        $row.IndexAttributes
    );
    
    $extLinks = Video::ExtLinks();
    
    $extLinksResult = $extLinks($row.Url, $numeratorResult.NumeratorEventsString);

    return AsStruct(
        $row.Url AS Url,
        $extLinksResult.OutLinks AS OutLinks,
        $extLinksResult.Error AS Error
    );
};
    
SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
