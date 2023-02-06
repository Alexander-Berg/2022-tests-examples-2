/* syntax version 1 */
$imagesPageParser = ImagesHtml::PageParser(
    FilePath("htparser.linktext.ini")
);

$numEvConv = NumEvConv::NumeratorEventsDeserializer();

$calc = ($row) -> {
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $imagesPageParserResult = $imagesPageParser(
        $numeratorResult.NumeratorEvents,
        $row.ZoneImgData,
        $row.SegmentatorResult,
        CAST($row.Charset AS INT32),
        $row.Url
    );

    return AsStruct(
        $row.Url as Url,
        $imagesPageParserResult.ImageLinks as ImageLinks,
        $imagesPageParserResult.HasMainContent as HasMainContent,
        $imagesPageParserResult.Title as Title,
        $imagesPageParserResult.SchemaOrg as SchemaOrg,
        $imagesPageParserResult.SchemaOrgProducts as SchemaOrgProducts
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
