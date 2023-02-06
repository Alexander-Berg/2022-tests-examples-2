/* syntax version 1 */
$EntitySearch = Annotator::EntitySearch(FolderPath("ner_data"), AsStruct(True as TestMode));

SELECT $EntitySearch(TableRow())
FROM Input;
