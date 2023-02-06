/* syntax version 1 */
$documentDate = Prewalrus::DocumentDate();

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $documentDateResult = $documentDate($row.Url, $numeratorResult.NumeratorEvents);

    return AsStruct(
        $row.Url AS Url,
        $documentDateResult.RecD AS RecD,
        $documentDateResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

