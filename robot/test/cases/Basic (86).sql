/* syntax version 1 */
$robotDater = Prewalrus::DateRobotExtractor();

$calc = ($row) -> {
    $robotDaterResult = $robotDater(
        $row.Url,
        $row.ParserChunks,
        $row.Language,
        $row.CrawlAddTime,
        $row.Charset,
        $row.LastAccess
    );

    return AsStruct(
        $row.Url AS Url,
        $robotDaterResult.RobotDate AS RobotDate,
        $robotDaterResult.RobotDateScore AS RobotDateScore,
        $robotDaterResult.RobotDateTimestamp AS RobotDateTimestamp,
        $robotDaterResult.RobotDateResult AS RobotDateResult,
        $robotDaterResult.Error AS Error
    );
};


SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

