/* syntax version 1 */
$udf = ImagesNN::FeaturesExtractorV1(FilePath("multihead_net_ver10.pb"), 8);
$getChunk = Images::GetChunk();

/* extsearch/images/protos/detectedobjects.proto @ */
$detectedObjectsListProto = AsAtom(@@{
    "name": "TDetectedObjectsListPB",
    "lists": {"optional":false},
    "meta": "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"
}@@);

$try_parse = YQL::Udf(AsAtom("Protobuf.TryParse"), Void(), Void(), $detectedObjectsListProto);

$calc = ($row) -> {
    $result = $udf($row.Thumbnail, $row.DetectedObjects);
    $chunk5 = $getChunk($result.KiwiWormRecord, "TDetectedObjectsChunkVer5");
    $chunk7 = $getChunk($result.KiwiWormRecord, "TDetectedObjectsChunkVer7");
    return AsStruct($result.KiwiWormRecord AS KiwiWormRecord,
                    $result.Error AS Error,
                    Yson::From($try_parse($chunk5.Chunk)) AS Chunk5,
                    Yson::From($try_parse($chunk7.Chunk)) AS Chunk7,
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
