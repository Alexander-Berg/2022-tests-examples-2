/* syntax version 1 */

$parser = Prewalrus::Parser();

$calc = ($row) -> {
    $url = $row.Host || $row.Path;

    $parserResult = $parser(
        $row.HttpBody,
        $url
    );

    return AsStruct(
        $url AS Url,
        Digest::Md5Hex($parserResult.ParserChunks) AS ParserChunksMd5,
        $parserResult.Error AS Error
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
