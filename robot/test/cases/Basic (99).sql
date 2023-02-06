/* syntax version 1 */
$textFeature = Prewalrus::TextFeature();

$calc = ($row) -> {
    $numEvConv = NumEvConv::NumeratorEventsDeserializer();
    $numeratorResult = $numEvConv($row.NumeratorEvents);

    $textFeatureResult = $textFeature(
        $row.Url,
        $numeratorResult.NumeratorEvents,
        $row.ZoneData
    );

    return AsStruct(
        $row.Url AS Url,
        $textFeatureResult.TextF AS TextF,
        $textFeatureResult.TextL AS TextL,
        $textFeatureResult.RusWordsInText AS RusWordsInText,
        $textFeatureResult.RusWordsInTitle AS RusWordsInTitle,
        $textFeatureResult.MeanWordLength AS MeanWordLength,
        $textFeatureResult.PercentWordsInLinks AS PercentWordsInLinks,
        $textFeatureResult.PercentVisibleContent AS PercentVisibleContent,
        $textFeatureResult.PercentFreqWords AS PercentFreqWords,
        $textFeatureResult.PercentUsedFreqWords AS PercentUsedFreqWords,
        $textFeatureResult.TrigramsProb AS TrigramsProb,
        $textFeatureResult.TrigramsCondProb AS TrigramsCondProb,
        $textFeatureResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

