/* syntax version 1 */

$imageExtMetaUpdate = Images::KiwiRec2TImageExtMetaUpdate();

SELECT Images::PrintProto("TImageMetaData", ImageMetaData) as ImageMetaData,
       IF(Images::PrintProto("TImageMetaData", ImageExtMetaUpdate.ImageMetaData) == Images::PrintProto("TImageMetaData", ImageMetaData), "EQUALS", "FAIL") as Same,
       ImageExtMetaUpdate.Url as Url,
       ImageExtMetaUpdate.ZoraCtx as ZoraCtx
FROM (
    SELECT Images::KiwiRec2ImageMetaData(KiwiRec, AsList(12)) as ImageMetaData,
           $imageExtMetaUpdate(KiwiRec, AsList(12)) as ImageExtMetaUpdate
    FROM Input
)
;
