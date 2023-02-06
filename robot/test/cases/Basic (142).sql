/* syntax version 1 */
$videoXmlParser = Video::XmlParser();

$calc = ($row) -> {
    $videoXmlParserResult = $videoXmlParser(
        $row.Url,
        $row.LastAccess,
        $row.MimeType,
        $row.OriginalDoc
    );

    return AsStruct(
        $row.Url AS Url,
        $videoXmlParserResult.Media AS Media,
        $videoXmlParserResult.IsBlocked AS IsBlocked,
        $videoXmlParserResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
