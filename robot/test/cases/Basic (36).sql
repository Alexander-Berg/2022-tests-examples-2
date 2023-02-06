/* syntax version 1 */
$udf = ImagesPic::BasicSignatures();

$calc = ($row) -> {
    $result = $udf($row.Thumbnail, $row.GenericImageAttrs, $row.ImageCrc);

    return AsStruct(
        $result.Error as Error,
        $result.ThumbnailHeader as ThumbnailHeader,
        $result.AnnotationFD as AnnotationFD,
        $result.Bars as Bars,
        $result.ColorStatsChunk as ColorStatsChunk,
        $result.ColornessChunk as ColornessChunk,
        $result.HistogramChunk as HistogramChunk,
        $result.ImageAttributes as ImageAttributes,
        $result.ImageIndexAttributes as ImageIndexAttributes,
        $result.ImageMD5Chunk as ImageMD5Chunk,
        $result.ImgExtSemidupSigNew as ImgExtSemidupSigNew,
        $result.ImgExtSemidupSigOld as ImgExtSemidupSigOld,
        $result.KiwiKeyChunk as KiwiKeyChunk,
        $result.PackedExtImageAttributes as PackedExtImageAttributes,
        $result.QualityChunk as QualityChunk,
        $result.QuantizedLocalDescriptorsShortChunk as QuantizedLocalDescriptorsShortChunk
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

