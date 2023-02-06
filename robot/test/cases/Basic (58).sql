/* syntax version 1 */
$extbreak = Prewalrus::ExtBreak();

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $extbreakResult = $extbreak($numeratorResult.NumeratorEvents, $row.ZoneData);

    return AsStruct(
        $row.Url AS Url,
        $extbreakResult.Breaks AS Breaks,
        $extbreakResult.LongText AS LongText,
        $extbreakResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

