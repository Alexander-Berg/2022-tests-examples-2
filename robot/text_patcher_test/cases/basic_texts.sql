/* syntax version 1 */
$text_patcher = Annotator::TextPatcher(FolderPath("text-patcher-data"), AsStruct(True as TestMode));

SELECT $text_patcher(TableRow())
FROM Input;
