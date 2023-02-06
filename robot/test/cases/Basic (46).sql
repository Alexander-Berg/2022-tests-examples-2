/* syntax version 1 */
$disambmask = Prewalrus::DisambMask();
$dtConv = DtConv::DirectTextDeserializer();

$calc = ($row) -> {

    $directTextResult = $dtConv($row.DirectTextEntries);

    $disambmaskResult = $disambmask($directTextResult.DirectText);

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($disambmaskResult.DisambMask) AS DisambMaskMd5
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

