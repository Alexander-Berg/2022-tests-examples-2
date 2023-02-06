/* syntax version 1 */
$sitemapParser = Sitemaps::SitemapParser();

$calc = ($row) -> {
    $result = $sitemapParser($row.ResponseBody, $row.MimeType);

    return AsStruct(
        $row.Url as Url,
        $result.Urls as Urls,
        $result.ParseErrors as ParseErrors,
        $result.IsIndex as IsIndex,
        $result.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

