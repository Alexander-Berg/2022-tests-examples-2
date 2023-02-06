/* syntax version 1 */
$shop = Prewalrus::Shop(
    FolderPath("shop")
);

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $shopResult = $shop($numeratorResult.NumeratorEvents);

    return AsStruct(
        $row.Url AS Url,
        $shopResult.IsShop AS IsShop,
        $shopResult.IsReview AS IsReview,
        $shopResult.Error AS Error
    );
};

SELECT * FROM
   (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

