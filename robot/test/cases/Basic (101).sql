/* syntax version 1 */
$title = Prewalrus::Title();

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $titleResult = $title(
        $numeratorResult.NumeratorEvents,
        $row.ZoneData
    );

    return AsStruct(
        $row.Url AS Url,
        $titleResult.Title AS Title,
        $titleResult.TitleCRC AS TitleCRC,
        $titleResult.TitleRawUTF8 AS TitleRawUTF8,
        $titleResult.TitleNormalizedUTF8 AS TitleNormalizedUTF8,
        $titleResult.Error AS Error 
    );
};

SELECT * FROM
   (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

