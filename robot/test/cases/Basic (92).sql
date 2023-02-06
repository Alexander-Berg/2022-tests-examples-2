/* syntax version 1 */
$simhash = Prewalrus::Simhash();

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $simhashResult = $simhash($numeratorResult.NumeratorEvents, $row.ZoneData);

    return AsStruct(
        $row.Url AS Url,
        $simhashResult.SimhashVersion AS SimhashVersion,
        $simhashResult.Simhash AS Simhash,
        $simhashResult.SimhashDocLength AS SimhashDocLength,
        $simhashResult.SimhashTitleHash AS SimhashTitleHash,
        Digest::Md5Hex($simhashResult.SimhashData) AS SimhashDataMd5,
        $simhashResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

