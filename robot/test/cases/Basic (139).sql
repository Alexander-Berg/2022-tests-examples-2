/* syntax version 1 */
$videoVtNumerator = Video::VtNumerator();

$numEvConv = NumEvConv::NumeratorEventsDeserializer();

$calc = ($row) -> {
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $videoVtNumeratorResult = $videoVtNumerator(
        $numeratorResult.NumeratorEvents,
        $row.Url,
        $row.LinkerConfig
    );

    return AsStruct(
        $videoVtNumeratorResult.Media AS VideoText,
        $videoVtNumeratorResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
