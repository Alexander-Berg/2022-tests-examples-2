/* syntax version 1 */
$metaDescriptionIndexData = Prewalrus::MetaDescriptionIndexData(
    FolderPath("queryrec"),
);

$calc = ($row) -> {
    $metaDescriptionIndexDataResult = $metaDescriptionIndexData($row.AnnSiteData);

    return AsStruct(
        $row.Url AS Url,
        $metaDescriptionIndexDataResult.AnnKeyInvZ AS AnnKeyInvZ,
        $metaDescriptionIndexDataResult.AnnRow AS AnnRow,
        $metaDescriptionIndexDataResult.AnnSentenceLengths AS AnnSentenceLengths,
        $metaDescriptionIndexDataResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

