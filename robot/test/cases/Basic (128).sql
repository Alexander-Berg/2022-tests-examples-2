/* syntax version 1 */
$videoNeuralNet = VideoImage::NeuralNet(FolderPath("videoneuralnettrigger"));

$calc = ($row) -> {
    $makeStable = True;
    $videoNeuralNetResult = $videoNeuralNet($row.Thumbnail, $row.ImageAttrs, $row.ImageCrc, $row.`Timestamp`, $makeStable);

    return AsStruct(
        $videoNeuralNetResult.ProbsAndFeatures AS ProbsAndFeatures,
        $videoNeuralNetResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
