/* syntax version 1 */
$price = Prewalrus::Price();
$dtConv = DtConv::DirectTextDeserializer();

$calc = ($row) -> {
    $directTextResult = $dtConv($row.DirectTextEntries);

    $priceResult = $price($directTextResult.DirectText);

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($priceResult.PricesDocAttrs) AS PricesDocAttrsMd5,
        $priceResult.PricesString AS PricesString,
        $priceResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

