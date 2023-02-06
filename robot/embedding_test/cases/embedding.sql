/* syntax version 1 */
$processor = Annotator::Embedding(FolderPath("data"), AsStruct(True as TestMode));

SELECT $processor(TableRow())
FROM Input;
