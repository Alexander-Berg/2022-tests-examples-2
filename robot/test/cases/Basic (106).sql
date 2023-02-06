/* syntax version 1 */
$yaPreview = Prewalrus::YaPreview();

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $yaPreviewResult = $yaPreview(
        $numeratorResult.NumeratorEvents,
        $row.ZoneData
    );

    return AsStruct(
        $row.Url AS Url,
        $yaPreviewResult.YaPreviewResult AS YaPreviewResult,
        $yaPreviewResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

