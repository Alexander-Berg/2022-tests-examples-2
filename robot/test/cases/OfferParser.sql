/* syntax version 1 */
$offerParser = Commercial::OfferParser(
    FilePath("config.json")
);

SELECT
    $offerParser(html, url, charset, timestampint64, setDisableFlag, "", EcomFeatures, false, "", 0, ZoraCtx, /*wantDebugString=*/true) AS serializedOffer
FROM Input;
