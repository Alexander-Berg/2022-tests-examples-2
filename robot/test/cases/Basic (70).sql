/* syntax version 1 */
$metaDescr = Prewalrus::MetaDescr(
    FilePath("dict.dict"),
    FilePath("stopword.lst")
);

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $metaDescrResult = $metaDescr(
        $numeratorResult.NumeratorEvents,
        $row.ZoneData,
        $row.Charset,
        $row.Language,
        $row.Url
    );

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($metaDescrResult.MetaDescrResult) AS MetaDescrResultMd5,
        Digest::Md5Hex($metaDescrResult.AnnSiteData) AS AnnSiteDataMd5,
        $metaDescrResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

