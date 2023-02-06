/* syntax version 1 */
$phoneNumber = Prewalrus::PhoneNumber(
    FilePath("phone_markers.gzt.bin")
);

$calc = ($row) -> {
    $dtConv = DtConv::DirectTextDeserializer();
    $directTextResult = $dtConv($row.DirectTextEntries);

    $phoneNumberResult = $phoneNumber($directTextResult.DirectText);

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($phoneNumberResult.PhonesDocAttrs) AS PhonesDocAttrsMd5,
        $phoneNumberResult.PhonesString AS PhonesString,
        $phoneNumberResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

