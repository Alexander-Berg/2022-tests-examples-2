/* syntax version 1 */
$dssmUrlTitleModelFeaturesSos = Prewalrus::DssmUrlTitleModelFeatures(
    FilePath("sos.dssm")
);

$dssmUrlTitleModelFeaturesMed = Prewalrus::DssmUrlTitleModelFeatures(
    FilePath("med.dssm")
);

$dssmUrlTitleModelFeaturesFinLaw = Prewalrus::DssmUrlTitleModelFeatures(
    FilePath("fin_law.dssm")
);

$dssmUrlTitleModelFeaturesCruelty = Prewalrus::DssmUrlTitleModelFeatures(
    FilePath("cruelty.dssm")
);

$dssmUrlTitleModelFeaturesMedWithTrash = Prewalrus::DssmUrlTitleModelFeatures(
    FilePath("med_with_trash.dssm")
);

$dssmUrlTitleModelFeaturesFinLawWithTrash = Prewalrus::DssmUrlTitleModelFeatures(
    FilePath("fin_law_with_trash.dssm")
);

$dssmUrlTitleModelFeaturesPageQualityClassifier = Prewalrus::DssmUrlTitleModelFeatures(
    FilePath("pq_url_title_classifier_v_oldtwo.dssm")
);

$dssmUrlTitleModelFeaturesPageQualitySlot2 = Prewalrus::DssmUrlTitleModelFeatures(
    FilePath("pq_slot2.dssm")
);

$to_str = ($v) -> {
    $s = 1e-5;
    $v2 = cast($v / $s as int64) * $s;
    return cast($v2 as string);
};

$calc = ($row) -> {
    $dssmUrlTitleModelFeaturesSosResult = $dssmUrlTitleModelFeaturesSos(
        $row.Url,
        $row.Title
    );

    $dssmUrlTitleModelFeaturesMedResult = $dssmUrlTitleModelFeaturesMed(
        $row.Url,
        $row.Title
    );

    $dssmUrlTitleModelFeaturesFinLawResult = $dssmUrlTitleModelFeaturesFinLaw(
        $row.Url,
        $row.Title
    );

    $dssmUrlTitleModelFeaturesCrueltyResult = $dssmUrlTitleModelFeaturesCruelty(
        $row.Url,
        $row.Title
    );

    $dssmUrlTitleModelFeaturesMedWithTrashResult = $dssmUrlTitleModelFeaturesMedWithTrash(
        $row.Url,
        $row.Title
    );

    $dssmUrlTitleModelFeaturesFinLawWithTrashResult = $dssmUrlTitleModelFeaturesFinLawWithTrash(
        $row.Url,
        $row.Title
    );

    $dssmUrlTitleModelFeaturesPageQualityClassifierResult = $dssmUrlTitleModelFeaturesPageQualityClassifier(
        $row.Url,
        $row.Title
    );

    $dssmUrlTitleModelFeaturesPageQualitySlot2Result = $dssmUrlTitleModelFeaturesPageQualitySlot2(
        $row.Url,
        $row.Title
    );

    return AsStruct(
        $row.Url AS Url,
        $row.Title AS Title,
        $to_str($dssmUrlTitleModelFeaturesSosResult.Prediction) AS SosPrediction,
        $dssmUrlTitleModelFeaturesSosResult.Error AS SosError,
        $to_str($dssmUrlTitleModelFeaturesMedResult.Prediction) AS MedPrediction,
        $dssmUrlTitleModelFeaturesMedResult.Error AS MedError,
        $to_str($dssmUrlTitleModelFeaturesFinLawResult.Prediction) AS FinLawPrediction,
        $dssmUrlTitleModelFeaturesFinLawResult.Error AS FinLawError,
        $to_str($dssmUrlTitleModelFeaturesCrueltyResult.Prediction) AS CrueltyPrediction,
        $dssmUrlTitleModelFeaturesCrueltyResult.Error AS CrueltyError,
        $to_str($dssmUrlTitleModelFeaturesMedWithTrashResult.Prediction) AS MedWithTrashPrediction,
        $dssmUrlTitleModelFeaturesMedWithTrashResult.Error AS MedWithTrashError,
        $to_str($dssmUrlTitleModelFeaturesFinLawWithTrashResult.Prediction) AS FinLawWithTrashPrediction,
        $dssmUrlTitleModelFeaturesFinLawWithTrashResult.Error AS FinLawWithTrashError,
        $to_str($dssmUrlTitleModelFeaturesPageQualityClassifierResult.Prediction) AS PageQualityClassifierPrediction,
        $dssmUrlTitleModelFeaturesPageQualityClassifierResult.Error AS PageQualityClassifierError,
        $to_str($dssmUrlTitleModelFeaturesPageQualitySlot2Result.Prediction) AS PageQualitySlot2Prediction,
        $dssmUrlTitleModelFeaturesPageQualitySlot2Result.Error AS PageQualitySlot2Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
