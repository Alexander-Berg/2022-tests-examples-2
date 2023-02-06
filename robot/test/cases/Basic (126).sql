/* syntax version 1 */
$videoMetaParser = Video::MetaParser();
$videoMediaToJson = Video::MediaToJson();
$numEvConv = NumEvConv::NumeratorEventsDeserializer();

$calc = ($row) -> {

    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $videoMetaParserResult = $videoMetaParser(
        $numeratorResult.NumeratorEvents,
        NULL,
        $row.Url,
        CAST($row.Charset AS UINT32)
    );

    return AsStruct(
        $row.Url AS Url,
        $videoMediaToJson($videoMetaParserResult.Media) AS Media,
        $videoMediaToJson($videoMetaParserResult.MediaUnchecked) AS MediaUnchecked,
        $videoMetaParserResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
