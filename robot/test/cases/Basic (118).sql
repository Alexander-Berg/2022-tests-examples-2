/* syntax version 1 */
$videoJsonLdExtractor = Video::JsonLdExtractor();

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $videoJsonLdExtractorResult = $videoJsonLdExtractor($numeratorResult.NumeratorEvents);

    return AsStruct(
        $row.Url AS Url,
        $videoJsonLdExtractorResult.JsonLd AS JsonLd,
        $videoJsonLdExtractorResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
