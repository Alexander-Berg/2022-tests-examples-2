/* syntax version 1 */
$dssmBlenderNewsJudgement = Prewalrus::DssmBlenderNewsJudgement();

$to_str = ($v) -> {
    $s = 1e-5;
    $v2 = cast($v / $s as int64) * $s;
    return cast($v2 as string);
};

$calc = ($row) -> {
    $dssmBlenderNewsJudgementResult = $dssmBlenderNewsJudgement(
        $row.Title
    );

    return AsStruct(
        $row.Title AS Title,
        $to_str($dssmBlenderNewsJudgementResult.Result) AS Result,
        $dssmBlenderNewsJudgementResult.Error AS Error
   );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;

