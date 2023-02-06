/* syntax version 1 */
$segmentator = Prewalrus::Segmentator(
    FilePath("2ld.list")
);

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $segmentatorResult = $segmentator($row.Url, $numeratorResult.NumeratorEvents, $row.ZoneData);

    return AsStruct(
        $row.Url AS Url,
        $segmentatorResult.SegmentAuxSpacesInText AS SegmentAuxSpacesInText,
        $segmentatorResult.SegmentAuxAlphasInText AS SegmentAuxAlphasInText,
        $segmentatorResult.SegmentContentCommasInText AS SegmentContentCommasInText,
        $segmentatorResult.SegmentWordPortionFromMainContent AS SegmentWordPortionFromMainContent,
        Digest::Md5Hex($segmentatorResult.SegmentatorResult) AS SegmentatorResultMd5,
        $segmentatorResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

