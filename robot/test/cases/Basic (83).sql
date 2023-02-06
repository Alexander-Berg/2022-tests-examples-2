/* syntax version 1 */
$queryFactor = Prewalrus::QueryFactor(
    FolderPath("pornofilter"),
);

$calc = ($row) -> {
    $dtConv = DtConv::DirectTextDeserializer();
    $directTextResult = $dtConv($row.DirectTextEntries);

    $queryFactorResult = $queryFactor(
        $directTextResult.DirectText
    );

    return AsStruct(
        $row.Url AS Url,
        $queryFactorResult.IsComm AS IsComm,
        $queryFactorResult.HasPayments AS HasPayments,
        $queryFactorResult.IsSEO AS IsSEO,
        $queryFactorResult.IsPorno AS IsPorno,
        $queryFactorResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

