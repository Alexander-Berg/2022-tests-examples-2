/* syntax version 1 */
$dataExtractor = RichSnippets::DataExtractor();

$calc = ($row) -> {
    $dataExtractorResult = $dataExtractor(
        $row.Url,
        $row.Charset,
        $row.NumeratorEvents
    );

    return AsStruct(
        $row.Url AS Url,
        $dataExtractorResult.Flags AS Flags,
        $dataExtractorResult.SchemaOrg AS SchemaOrg,
        $dataExtractorResult.Semantic2Json AS Semantic2Json,
        $dataExtractorResult.Recipe AS Recipe,
        $dataExtractorResult.ProductOffer AS ProductOffer,
        $dataExtractorResult.VideoObject AS VideoObject,
        $dataExtractorResult.YoutubeChannel AS YoutubeChannel,
        $dataExtractorResult.SoftwareAppImg AS SoftwareAppImg,
        $dataExtractorResult.Error AS Error
    );
};

SELECT * FROM
   (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

