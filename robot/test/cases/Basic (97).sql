/* syntax version 1 */
$tasixhost = Prewalrus::TasixHost(
    FilePath("tasix_hosts.txt")
);

$calc = ($row) -> {
    $tasixhostResult = $tasixhost($row.Url);

    return AsStruct(
        $row.Url AS Url,
        $tasixhostResult.TasixHostAttrs AS TasixHostAttrs,
        $tasixhostResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

