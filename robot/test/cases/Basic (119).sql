/* syntax version 1 */
$videoLinksExtractor = Video::LinksExtractor(FolderPath("links_extractor_config_dir"));

$calc = ($row) -> {

    $videoLinksExtractorResult = $videoLinksExtractor(
        $row.Media,
        $row.Embed,
        $row.Sitemap,
        $row.MetaThreshold
    );

    return AsStruct(
        $row.Url AS Url,
        $videoLinksExtractorResult.VideoLinks AS VideoLinks,
        $videoLinksExtractorResult.VideoApiLinks AS VideoApiLinks,
        $videoLinksExtractorResult.ThumbLinks AS ThumbLinks,
        $videoLinksExtractorResult.WebLinks AS WebLinks,
        $videoLinksExtractorResult.MetarobotLinks AS MetarobotLinks,
        $videoLinksExtractorResult.RecrawlLinkAttrs AS RecrawlLinkAttrs,
        $videoLinksExtractorResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
