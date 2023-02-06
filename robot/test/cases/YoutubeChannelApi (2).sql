/* syntax version 1 */
$authorJsonApi = Video::AuthorJsonApi(FolderPath("author_json_api"));
$authorLinksExtractor = Video::AuthorLinksExtractor();
$urlExtractor = Video::UrlExtractor();

$calc1 = ($row) -> {

    $authorJsonApiResult = $authorJsonApi($row.Url, NULL, $row.`Json`);
    $authorLinksExtractorResult = $authorLinksExtractor($authorJsonApiResult.Author);

    return AsStruct(
        $row.Url AS Url,
        $authorLinksExtractorResult.VideoLinks AS VideoLinks,
        $authorLinksExtractorResult.VideoApiLinks AS VideoApiLinks,
        $authorLinksExtractorResult.ThumbLinks AS ThumbLinks,
        $authorLinksExtractorResult.WebLinks AS WebLinks,
        $authorLinksExtractorResult.MetarobotLinks AS MetarobotLinks,
        $authorLinksExtractorResult.RecrawlAttrs AS RecrawlAttrs,
        $authorLinksExtractorResult.Error AS Error
    );
};

$calc2 = ($row) -> {
    $res = $calc1($row);

    return AsStruct(
        $row.Url AS Url,
        $urlExtractor($row.Url, $res.VideoLinks) AS VideoLinks,
        $urlExtractor($row.Url, $res.VideoApiLinks) AS VideoApiLinks,
        $urlExtractor($row.Url, $res.ThumbLinks) AS ThumbLinks,
        $urlExtractor($row.Url, $res.WebLinks) AS WebLinks,
        $urlExtractor($row.Url, $res.MetarobotLinks) AS MetarobotLinks
    );
};

SELECT * FROM
    (SELECT $calc1(TableRow()) FROM Input)
FLATTEN COLUMNS
;

SELECT * FROM
    (SELECT $calc2(TableRow()) FROM Input)
FLATTEN COLUMNS
;
