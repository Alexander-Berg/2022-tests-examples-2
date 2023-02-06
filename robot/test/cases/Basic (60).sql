/* syntax version 1 */
$freqCalculator = Prewalrus::FreqCalculator();
$dtConv = DtConv::DirectTextDeserializer();

$calc = ($row) -> {
    $directTextResult = $dtConv($row.DirectTextEntries);

    $freqCalculatorResult = $freqCalculator($directTextResult.DirectText);

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($freqCalculatorResult.FreqCalculatorResult) AS FreqCalculatorResultMd5,
        Digest::Md5Hex($freqCalculatorResult.DataArray) AS DataArrayMd5,
        $freqCalculatorResult.Error AS Error
    );
};

SELECT * FROM
   (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

