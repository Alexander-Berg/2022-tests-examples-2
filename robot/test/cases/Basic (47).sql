/* syntax version 1 */
$docSize = Prewalrus::DocSize();

$calc = ($row) -> {
    $docSizeResult = $docSize($row.IndexPortions);

    return AsStruct(
        $row.Url AS Url,
        $docSizeResult.DocSize AS DocSize,
        $docSizeResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

