/* syntax version 1 */
$compactKeyInv = Prewalrus::CompactKeyInv();

$calc = ($row) -> {
    $compactKeyInvResult = $compactKeyInv($row.IndexPortions);

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($compactKeyInvResult.KeyInvZ) AS KeyInvZMd5,
        $compactKeyInvResult.Error AS Error
    );
};
  
SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

