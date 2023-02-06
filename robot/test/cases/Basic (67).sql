/* syntax version 1 */
$maxFreq = Prewalrus::MaxFreq();

$calc = ($row) -> {
    $maxFreqResult = $maxFreq($row.DataArray);

    return AsStruct(
        $row.Url AS Url,
        $maxFreqResult.MaxFreq AS MaxFreq,
        $maxFreqResult.Error AS Error
    );
};

SELECT * FROM
   (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

