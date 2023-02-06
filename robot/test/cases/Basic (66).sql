/* syntax version 1 */
$longSimhash = Prewalrus::LongSimHash();
$dtConv = DtConv::DirectTextDeserializer();

$calc = ($row) -> {
    $directTextResult = $dtConv($row.DirectTextEntries);

    $longSimhashResult = $longSimhash($directTextResult.DirectText, $row.SegmentatorResult);

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($longSimhashResult.Result) AS LongSimhashMd5,
        $longSimhashResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

