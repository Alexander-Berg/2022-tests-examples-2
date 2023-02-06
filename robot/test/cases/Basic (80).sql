/* syntax version 1 */
$portionsPrint = Prewalrus::PortionsPrint();

$calc = ($row) -> {
    $portionsPrintResult = $portionsPrint($row.KeyInvZ, "zlib+oki1");

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($portionsPrintResult.PortionsString) AS PortionsStringMd5,
        $portionsPrintResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

