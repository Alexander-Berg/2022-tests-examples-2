/* syntax version 1 */
$udf = ImagesOcr::OcrV2(FilePath("ocrdata.tar"));
$ocrExtract = ImagesOcr::OcrV2Extract();

$calc = ($row) -> {
    $ocrResult = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc, DateTime::FromSeconds(1531247547));

    $ocrExtractResult = $ocrExtract($ocrResult.KiwiWormRecord, False);
    $ocrExtractDebugResult = $ocrExtract($ocrResult.KiwiWormRecord, True);
    return AsStruct(
        $ocrResult.KiwiWormRecord AS OcrResults,
        $ocrResult.Error AS Error,
        $ocrExtractResult.Error AS ErrorParse,
        $ocrExtractResult.OcrStroka as OcrStroka,
        $ocrExtractDebugResult.OcrStroka as OcrStrokaDebug
   );
};
  
SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

