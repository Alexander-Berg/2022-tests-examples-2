/* syntax version 1 */
$numEvConv = NumEvConv::NumeratorEventsDeserializer();

$calc = ($row) -> {
    $numeratorResult = $numEvConv($row.NumeratorEvents);
    $videoSoft404Classifier = Video::Soft404Classifier(FilePath("soft404.conf"));
    $videoSoft404ClassifierResult = $videoSoft404Classifier(
        $numeratorResult.NumeratorEvents,
        $row.ZoneData,
        $row.Url,
       "{}"
    );

    return AsStruct(
        $row.Url AS Url,
        $videoSoft404ClassifierResult.IsSoft404 AS IsSoft404,
        $videoSoft404ClassifierResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
