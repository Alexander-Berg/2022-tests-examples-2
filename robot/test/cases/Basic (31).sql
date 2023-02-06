/* syntax version 1 */
$udf = ImagesOcr::Ocr(FilePath("ocrdata.tar"));
$ocrExtract = ImagesOcr::OcrExtract();

$calc = ($row) -> {
    $ocrResult = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc, DateTime::FromSeconds(1531247547));

    $ocrExtractResult = $ocrExtract($ocrResult.OcrResults, False);
    $ocrExtractDebugResult = $ocrExtract($ocrResult.OcrResults, True);
    return AsStruct(
        $ocrResult.OcrResults AS OcrResults,
        $ocrResult.Error AS Error,
        $ocrExtractResult.OcrStroka as OcrStroka,
        $ocrExtractDebugResult.OcrStroka as OcrStrokaDebug
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
