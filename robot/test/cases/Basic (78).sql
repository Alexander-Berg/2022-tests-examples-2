/* syntax version 1 */
$poetry = Prewalrus::Poetry(
    FilePath("forces_info")
);

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $poetryResult = $poetry(
        $numeratorResult.NumeratorEvents
    );

    return AsStruct(
        $row.Url AS Url,
        $poetryResult.Poetry AS Poetry,
        $poetryResult.Poetry2 AS Poetry2,
        $poetryResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

