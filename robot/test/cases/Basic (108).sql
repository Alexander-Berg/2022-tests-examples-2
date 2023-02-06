/* syntax version 1 */
$jsFactors = Rotor::JsFactors(
    FilePath("2ld.list")
);

$calc = ($row) -> {
    $jsFactorsResult = $jsFactors(
        $row.NumeratorEvents,
        $row.ZoneData
    );

    return AsStruct($jsFactorsResult.Factors AS Factors, $jsFactorsResult.Error AS Error);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

