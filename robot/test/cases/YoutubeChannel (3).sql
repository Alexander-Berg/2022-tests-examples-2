/* syntax version 1 */
$xpathParser = Video::XpathParser(FolderPath("xpath_parser"));

$calc = ($row) -> {
    $xpathParserResult = $xpathParser($row.Url, $row.Html);

    return AsStruct(
        $row.Url AS Url,
        $xpathParserResult.`Json` AS `Json`,
        $xpathParserResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
