/* syntax version 1 */
$videoUrlExtractor = Video::UrlExtractor();

$calc = ($row) -> {
    $videoLinksResult = $videoUrlExtractor($row.Url, $row.VideoLinks);
    $thumbLinksResult = $videoUrlExtractor($row.Url, $row.ThumbLinks);
    $error = $videoLinksResult.Error ?? $thumbLinksResult.Error;

    return AsStruct(
        $videoLinksResult.Url AS VideoLinksUrl,
        $thumbLinksResult.Url AS ThumbLinksUrl,
        $error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
