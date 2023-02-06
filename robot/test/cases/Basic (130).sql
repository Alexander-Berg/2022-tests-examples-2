/* syntax version 1 */
$videoRegexpExtractor = Video::RegexpExtractor(FilePath("regexps.re"), FilePath("player_regexps.re"));

$numEvConv = NumEvConv::NumeratorEventsDeserializer();

$calc = ($row) -> {
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $videoRegexpExtractorResult = $videoRegexpExtractor(
        $numeratorResult.NumeratorEvents,
        $row.ZoneData,
        $row.Url,
        CAST($row.IndexDate AS UINT32),
        CAST($row.Charset AS UINT32)
    );

    return AsStruct(
        $row.Url AS Url,
        $videoRegexpExtractorResult.Media AS Media,
        $videoRegexpExtractorResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
