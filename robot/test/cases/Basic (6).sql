$dssmEcomFeatures = Commercial::DssmEcomFeatures();

$calc = ($row) -> {
    $dssmEcomFeaturesResult = $dssmEcomFeatures(
        $row.Url,
        $row.Title,
        True,
    );

    return AsStruct(
        $row.Url AS Url,
        $dssmEcomFeaturesResult.Result AS ParsedResult,
        $dssmEcomFeaturesResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

