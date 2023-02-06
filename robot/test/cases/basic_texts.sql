/* syntax version 1 */
$commonParams = AsStruct(True as TestMode);

$calc = ($row) -> {
    $textPatcher = Annotator::TextPatcher(FolderPath("text-patcher-data"), $commonParams);
    $textPatcherResult = $textPatcher(AsStruct($row.Title AS Title, $row.Text AS Text));

    $passages = Annotator::Passages(FolderPath("passages-data"), $commonParams);
    $passagesResult = $passages(AsStruct($row.Title AS Title, $row.Text AS Text, $textPatcherResult.PatchedText AS PatchedText));

    $entitySearch = Annotator::EntitySearch(FolderPath("ner_data"), $commonParams);
    $entitySearchResult = $entitySearch(AsStruct($row.Title AS Title, $row.Text AS Text, $textPatcherResult.PatchedText AS PatchedText, $passagesResult.Passages as Passages));

    $embedding = Annotator::Embedding(FolderPath("embedding-data"), AsStruct($commonParams.TestMode as TestMode, True as OutputSerializedMessages));
    $embeddingResult = $embedding(AsStruct(
        $row.Title as Title,
        $row.Text as Text,
        $row.Url as Url,
        $textPatcherResult.PatchedText AS PatchedText,
        $passagesResult.Passages as Passages,
        $entitySearchResult.EntitysearchResult as EntitysearchResult,
    ));

    return AsStruct(
        $row.Url as Url,
        $textPatcherResult.PatchedText as PatchedText,
        $passagesResult.Passages as Passages,
        $entitySearchResult.EntitysearchResult as EntitysearchResult,
        $embeddingResult.Profile as Profile,
        $embeddingResult.SerializedProfile as SerializedProfile);
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

