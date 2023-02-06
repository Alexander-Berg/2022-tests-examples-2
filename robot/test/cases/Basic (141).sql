/* syntax version 1 */
$videoWildPlayer = Video::WildPlayer();

$numEvConv = NumEvConv::NumeratorEventsDeserializer();

$calc = ($row) -> {
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $videoWildPlayerResult = $videoWildPlayer($numeratorResult.NumeratorEvents);

    return AsStruct(
        $row.Url AS Url,
        $videoWildPlayerResult.OutLinks AS OutLinks,
        $videoWildPlayerResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
