/* syntax version 1 */
$Passages = Annotator::Passages(FolderPath("data"), AsStruct(True as TestMode));

SELECT $Passages(TableRow())
FROM Input;
