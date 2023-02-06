/* syntax version 1 */
$directText = Prewalrus::DirectText();

$calc = ($row) -> {

    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $directTextResult = $directText(
        $numeratorResult.NumeratorEvents,
        $row.ZoneData,
        $row.DocId,
        $row.UrlFlags,
        $row.Charset,
        $row.Language,
        $row.Language2,
        $row.IndexDate,
        $row.MimeType,
        $row.Url,
        $row.SegmentatorResult,
        $row.ExtraTextZones,
        $row.LemmaNormalization
    );

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($directTextResult.DirectTextString) AS DirectTextEntriesMd5,
        Digest::Md5Hex($directTextResult.DirectTextAttrs) AS DirectTextAttrsMd5,
        Digest::Md5Hex($directTextResult.Links) AS LinksMd5,
        $directTextResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

