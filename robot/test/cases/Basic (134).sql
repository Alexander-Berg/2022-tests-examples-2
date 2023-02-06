/* syntax version 1 */
$videoTextFactors = Video::TextFactors(
    FilePath("segments.lst"),
    FilePath("titles.lst")
);

$calc = ($row) -> {
    $videoTextFactorsResult = $videoTextFactors($row.Url, $row.Title);

    return AsStruct(
        $videoTextFactorsResult.UrlSegments AS UrlSegments,
        $videoTextFactorsResult.TitleWords AS TitleWords,
        $videoTextFactorsResult.Factors AS Factors,
        $videoTextFactorsResult.FactorsStr AS FactorsStr,
        $videoTextFactorsResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

