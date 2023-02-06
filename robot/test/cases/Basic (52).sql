/* syntax version 1 */
$dssmNavParasitesFeatures = Prewalrus::DssmNavParasitesFeatures(
    FilePath("nav_parasites.dssm")
);

$to_str = ($v) -> {
    $s = 1e-5;
    $v2 = cast($v / $s as int64) * $s;
    return cast($v2 as string);
};

$calc = ($row) -> {
    $dssmNavParasitesFeaturesResult = $dssmNavParasitesFeatures(
        $row.Url,
        $row.Title
    );

    return AsStruct(
        $row.Url AS Url,
        $to_str($dssmNavParasitesFeaturesResult.Prediction) AS Prediction,
        $dssmNavParasitesFeaturesResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
