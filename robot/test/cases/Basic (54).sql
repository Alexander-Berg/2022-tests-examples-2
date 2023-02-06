/* syntax version 1 */
$dssmProductsOnPageFeatures = Prewalrus::DssmProductsOnPageFeatures(
    FolderPath("JUPITER_DSSM_MODELS")
);

$to_str = ($v) -> {
    $s = 1e-5;
    $v2 = cast($v / $s as int64) * $s;
    return cast($v2 as string);
};

$calc = ($row) -> {
    $dssmProductsOnPageFeaturesResult = $dssmProductsOnPageFeatures(
        $row.Url,
        $row.Title
    );

    return AsStruct(
        $row.Url AS Url,
        $to_str($dssmProductsOnPageFeaturesResult.NoProductsProbability) AS NoProductsProbability,
        $to_str($dssmProductsOnPageFeaturesResult.OneProductProbability) AS OneProductProbability,
        $to_str($dssmProductsOnPageFeaturesResult.ManyProductsProbability) AS ManyProductsProbability,
        $dssmProductsOnPageFeaturesResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

