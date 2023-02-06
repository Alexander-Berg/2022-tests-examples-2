/* syntax version 1 */
$converter = Prewalrus::Converter(
    FilePath("dict.dict")
);

$calc = ($row) -> {

    $converterResult = $converter(
        $row.OriginalDoc,
        $row.MimeType
    );

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($converterResult.HtmlConv) AS HtmlConvMd5,
        $converterResult.MimeType AS MimeType,
        $converterResult.Charset AS Charset,
        $converterResult.Error AS Error
   );
};
  
SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

