/* syntax version 1 */
$newshost = Prewalrus::NewsHost(
    FilePath("news_hosts.txt")
);

$calc = ($row) -> {
    $newshostResult = $newshost($row.Url);

    return AsStruct(
        $row.Url AS Url,
        $newshostResult.NewsHostAttrs AS NewsHostAttrs,
        $newshostResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

