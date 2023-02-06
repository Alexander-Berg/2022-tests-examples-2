/* syntax version 1 */
$shingle = Prewalrus::Shingle();

$calc = ($row) -> {
    $shingleResult = $shingle($row.NumeratorEvents);

    return AsStruct(
        $shingleResult.Shingles AS Shingles,
        $shingleResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

