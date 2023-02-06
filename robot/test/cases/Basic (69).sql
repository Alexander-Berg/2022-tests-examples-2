/* syntax version 1 */
$mergeDataContainer = Prewalrus::MergeDataContainer();

$calc = ($row) -> {
    $mergeDataContainerResult = $mergeDataContainer(
        $row.MetaDescr,
        $row.UrlSeg,
        $row.MediaWiki,
        $row.YaPreview,
        $row.SchemaOrg,
        $row.LongSimhash
    );

    return AsStruct(
        $row.Url AS Url,
        Digest::Md5Hex($mergeDataContainerResult.MergedTDataContainer) AS MergedTDataContainerMd5,
        $mergeDataContainerResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

