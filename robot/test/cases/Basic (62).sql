/* syntax version 1 */
$indexingSource = Prewalrus::IndexingSource();

SELECT
    $indexingSource(IndexingSourceName).PackedSource AS PackedSource
FROM Input;
