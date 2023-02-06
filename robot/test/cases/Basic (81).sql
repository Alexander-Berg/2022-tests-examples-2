/* syntax version 1 */
$ppb = Prewalrus::Ppb(
    FilePath("ppb_hosts.txt")
);

$calc = ($row) -> {
    $ppbResult = $ppb($row.Url);

    return AsStruct(
        $row.Url AS Url,
        $ppbResult.IsForPpb AS IsForPpb,
        $ppbResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

