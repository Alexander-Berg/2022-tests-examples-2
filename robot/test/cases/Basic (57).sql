/* syntax version 1 */
$eshop = Prewalrus::EShop();

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $eshopResult = $eshop($numeratorResult.NumeratorEvents);

    return AsStruct(
        $row.Url AS Url,
        $eshopResult.Eshop AS Eshop,
        $eshopResult.EshopV AS EshopV,
        $eshopResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

