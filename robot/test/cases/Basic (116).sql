/* syntax version 1 */
$videoHtmlTagsParser = Video::HtmlTagsParser();

$numEvConv = NumEvConv::NumeratorEventsDeserializer();

$calc = ($row) -> {
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $videoHtmlTagsParserResult = $videoHtmlTagsParser(
        CAST($row.Encoding AS UINT32),
        $numeratorResult.NumeratorEvents,
        $row.ZoneData
    );

    return AsStruct(
        $row.Url AS Url,
        $videoHtmlTagsParserResult.HtmlTags AS HtmlTags,
        $videoHtmlTagsParserResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
