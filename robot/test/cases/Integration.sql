/* syntax version 1 */
$itdItpEligibility = Prewalrus::ItdItpEligibility(
    FolderPath("JUPITER_ITDITP_ELIGIBILITY_MODELS")
);

$calc = ($row) -> {
    $itdItpEligibilityResult = $itdItpEligibility($row.KeyInvz);

    return AsStruct(
        $row.KeyInvz AS KeyInvz,
        $itdItpEligibilityResult.ItdItpContentFeatures AS ItdItpContentFeatures,
        $itdItpEligibilityResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
