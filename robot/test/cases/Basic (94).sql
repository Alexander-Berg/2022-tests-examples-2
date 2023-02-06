/* syntax version 1 */
$simpleTextArc = Prewalrus::SimpleTextArc();

$calc = ($row) -> {
    $simpleTextArcResult = $simpleTextArc(
        $row.DirectTextEntries,
        $row.SegmentatorResult
    );

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($simpleTextArcResult.TextArchivePortion) AS SimpleTextArcMd5,
        $simpleTextArcResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

