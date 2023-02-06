/* syntax version 1 */
$tmuCalc = Tmu2::CreateTmuCalc();
$deduceCalc = Deduce::CreateDeduceCalc();
$deduceGetBool = Deduce::CreateDeduceGetBool("logpath=/dev/stderr", FolderPath("AntispamRules"));
$deduceGetInt = Deduce::CreateDeduceGetInt("logpath=/dev/stderr", FolderPath("AntispamRules"));
$deduceGetDouble = Deduce::CreateDeduceGetDouble("logpath=/dev/stderr", FolderPath("AntispamRules"));
$deduceGetString = Deduce::CreateDeduceGetString("logpath=/dev/stderr", FolderPath("AntispamRules"));
$antispamFeaturesRemap = Deduce::CreateAntispamFeaturesRemap(FolderPath("AntispamRules"));
$aspamLinksPessimizations = Deduce::CreateAspamLinksPessimizations(FolderPath("AntispamRules"));

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

    $deduceCalcResult = $deduceCalc(
        NVL($url, ""),
        NVL($tmuCalcResult.TmuData, ""),
        ""
    );

    $antispamFeaturesRemapResult = $antispamFeaturesRemap (
        NVL($deduceCalcResult.DeduceData, ""),
        NVL($deduceCalcResult.DeduceDataRevision, 0)
    );

    $aspamLinksPessimizationsResult = $aspamLinksPessimizations (
        NVL($deduceCalcResult.DeduceData, ""),
        NVL($deduceCalcResult.DeduceDataRevision, 0)
    );

    $allSpam = $deduceGetBool($deduceCalcResult.DeduceData, $deduceCalcResult.DeduceDataRevision, "ALL_SPAM").Value;
    $rtBan = $deduceGetInt($deduceCalcResult.DeduceData, $deduceCalcResult.DeduceDataRevision, "RT_ANTISPAM_BAN").Value;
    $nasty = $deduceGetDouble($deduceCalcResult.DeduceData, $deduceCalcResult.DeduceDataRevision, "PORNO_NEWRELEASE_2").Value;
    $footprint = $deduceGetString($deduceCalcResult.DeduceData, $deduceCalcResult.DeduceDataRevision, "FOOTPRINT").Value;

    return AsStruct(
        $url AS Url,
        $allSpam AS AllSpam,
        $rtBan AS RtBan,
        $nasty AS Nasty,
        $antispamFeaturesRemapResult.ErfPatch AS AntispamErf2Features,
        $aspamLinksPessimizationsResult.DsmFlags AS AspamLinksPessimizations,
        $deduceGetBool($deduceCalcResult.DeduceData, $deduceCalcResult.DeduceDataRevision, "ALL_SPAM").Value AS ALL_SPAM,
        $deduceGetBool($deduceCalcResult.DeduceData, $deduceCalcResult.DeduceDataRevision, "CY_EXCLUDE").Value AS CY_EXCLUDE,
        $deduceGetBool($deduceCalcResult.DeduceData, $deduceCalcResult.DeduceDataRevision, "FORUM_FULLBAD_DOC_BAN").Value AS FORUM_FULLBAD_DOC_BAN,
        $deduceGetBool($deduceCalcResult.DeduceData, $deduceCalcResult.DeduceDataRevision, "FORUM_DETECTOR").Value AS FORUM_DETECTOR
    );
};

SELECT * FROM
(SELECT $calc(TableRow()) FROM Input)
FLATTEN COLUMNS
;
