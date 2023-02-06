/* syntax version 1 */
$addressFilter = Prewalrus::AddressFilter(
    FilePath("streets.trie")
);

$calc = ($row) -> {

    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $addressFilterResult = $addressFilter(
        $numeratorResult.NumeratorEvents,
        $row.ZoneData
    );

    return AsStruct(
        $row.Url AS Url,
        $addressFilterResult.HasAddress AS HasAddress,
        $addressFilterResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
