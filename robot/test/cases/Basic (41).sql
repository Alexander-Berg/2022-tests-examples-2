/* syntax version 1 */
$alternateHreflangProcessor = Prewalrus::AlternateHreflang();

$calc = ($row) -> {
    $alternateHreflangResult = $alternateHreflangProcessor($row.AlternateHreflang);

    return AsStruct(
        $row.Url AS Url,
        $alternateHreflangResult.AlternateHreflang AS AlternateHreflang,
        $alternateHreflangResult.AlternateHreflangResult AS AlternateHreflangResult,
        $alternateHreflangResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

