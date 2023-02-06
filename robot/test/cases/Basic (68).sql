/* syntax version 1 */
$mediaWiki = Prewalrus::MediaWiki();

$numEvConv = NumEvConv::NumeratorEventsDeserializer();

$calc = ($row) -> {
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $mediaWikiResult = $mediaWiki($numeratorResult.NumeratorEvents);

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($mediaWikiResult.ZonesAndAttrs) AS ZonesAndAttrsMd5,
        $mediaWikiResult.StaticDescription AS StaticDescription,
        $mediaWikiResult.Error AS Error
   );
};

SELECT * FROM
   (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

