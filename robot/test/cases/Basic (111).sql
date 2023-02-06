/* syntax version 1 */
$videoDataFilter = Video::DataFilter();

$calc = ($row) -> {

    $videoDataFilterResult = $videoDataFilter($row.Media, $row.FilterTag);

    return AsStruct(
        $row.Url AS Url,
        $videoDataFilterResult.Media AS Media,
        $videoDataFilterResult.Error AS Error
    )
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
