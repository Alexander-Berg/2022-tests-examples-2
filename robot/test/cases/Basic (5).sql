/* syntax version 1 */
$tmuCalc = Tmu2::CreateTmuCalc();

$tmuDump = Tmu2::CreateTmuDump(
    "logprefix=tmudump;logpath=/dev/stderr",
    "AntispamRules"
);

$calc = ($row) -> {
    $url = NVL($row.Host, "") || NVL($row.Path, "");

    $tmuCalcResult = $tmuCalc(
        NVL($url, ""),
        NVL($row.Html, ""),
        NVL(CAST($row.MimeType AS Int32), -1),
        NVL(CAST($row.Charset AS Int32), -1),
        NVL(CAST($row.Language AS Int32), -1),
        NVL(CAST($row.LastAccess AS UInt64), 0),
        NVL(CAST($row.LastAccess AS UInt64), 0),
        NVL(CAST($row.HttpModTime AS UInt64), 0),
        NVL(CAST($row.LastAccess AS UInt64), 0),
        "",
        True
    );

    $tmuDumpResult = $tmuDump($tmuCalcResult.TmuData);

    return AsStruct(
        $url AS Url,
        $tmuCalcResult.TmuData AS TmuDataYql,
        $tmuDumpResult AS TmuDumpYql
    );
};

SELECT * FROM
    (SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
