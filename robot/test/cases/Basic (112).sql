/* syntax version 1 */
$videoDataMerge = Video::DataMerge();

$calc = ($row) -> {

    $videoDataMergeResult = $videoDataMerge(
        $row.Media,
        $row.Url,
        $row.LangRegion,
        $row.WebAddTime,
        $row.NoIndex,
        $row.LastAccess,
        $row.SimhashVersion,
        $row.Simhash,
        $row.SimhashDocLength,
        $row.SimhashTitleHash
    );

    return AsStruct(
        $row.Url AS Url,
        $videoDataMergeResult.Media AS Media,
        $videoDataMergeResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
