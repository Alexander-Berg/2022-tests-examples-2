/* syntax version 1 */
$videoPageParser = Video::PageParser(
    FilePath("uselessflash.lst"),
    FilePath("htparser.linktext.ini"),
    FilePath("url_generators.def"),
    FilePath("url_generators.flashvars")
);

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $videoPageParserResult = $videoPageParser(
        $numeratorResult.NumeratorEvents,
        $row.ZoneImgData,
        $row.SegmentatorResult,
        CAST($row.Charset AS INT32),
        $row.Url
    );

    return AsStruct(
        $row.Url AS Url,
        $videoPageParserResult.Embed AS Embed,
        $videoPageParserResult.Media AS Media,
        $videoPageParserResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
