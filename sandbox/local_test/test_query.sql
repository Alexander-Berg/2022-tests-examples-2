pragma yt.TmpFolder = "//tmp";

use hahn;
--TODO: use pool to speed up YQL
--pragma yt.Pool = "yabs-cs";

$segment_traffic_type_table = "//home/comdep-analytics/YAN/segmentation/static/latest/blocks";
$page_dsp_table = "//home/yabs-cs/key_1/v2/export/CaesarPage/PageDSP.last";
$page_partner_share_table = "//home/yabs/dict/PagePartnerShare";
$partner_page_table = "//home/yabs/dict/PartnerPage";
$turnover_table = "//home/yabs/tac-manager/tmp/turnover/turnover_2022_02_02";

$CurrentPartnerShareFrom = 0;
$CurrentPartnerShareTo = 1000000;
$NewPartnerShare = NULL;
$DeltaPartnerShare = 20000;

--- FILTER PageDSP

$page_dsp = 
SELECT
    pd.DSPID AS DSPID,
    pd.PageID AS PageID,
    pd.ImpID AS ImpID,
    pd.PartnerShare AS PartnerShare,
    s.segment AS Segment,
    pp.PartnerID AS PartnerID,
    pp.Login AS Login,
    String::SplitToList(pp.DomainList, ",")[0] AS Domain
FROM $page_dsp_table AS pd
LEFT JOIN $segment_traffic_type_table AS s ON (
    pd.PageID = s.page_id AND 
    pd.ImpID = s.block_id
)
LEFT JOIN $partner_page_table AS pp ON (
    pd.PageID = pp.PageID
)

;

$page_dsp_filtered = 
SELECT *
FROM $page_dsp
WHERE
    PageID in (414314) AND
    (PageID,ImpID) in ((1,2),(3,4),(5,6)) AND
    Segment in ("tier-1") AND

    PartnerShare>=$CurrentPartnerShareFrom AND
    PartnerShare<=$CurrentPartnerShareTo
;

$pages_filtered =
SELECT DSPID, PageID
FROM $page_dsp_filtered
GROUP BY DSPID, PageID;

$pages_filtered_hash =
SELECT * FROM (
    SELECT 
        DSPID,
        PageID,
        COUNT(DISTINCT PartnerShare) AS PartnerShareCount,
        COUNT(*) AS ImpCount,
        SUM(CAST(ImpID AS Uint64)) AS ImpHash,
        SOME(PartnerShare) AS PartnerShare
    FROM $page_dsp_filtered
    GROUP BY DSPID, PageID
) WHERE PartnerShareCount = 1;

$pages_hash =
SELECT * FROM (
    SELECT 
        pd.DSPID AS DSPID,
        pd.PageID AS PageID,
        COUNT(DISTINCT pd.PartnerShare) AS PartnerShareCount,
        COUNT(*) AS ImpCount,
        SUM(CAST(pd.ImpID AS Uint64)) AS ImpHash
    FROM $page_dsp AS pd
    INNER JOIN $pages_filtered AS pf
    ON (pf.DSPID = pd.DSPID AND pf.PageID = pd.PageID)
    GROUP BY pd.DSPID, pd.PageID
) WHERE PartnerShareCount = 1;

$pages_consistent =
SELECT 
    h.DSPID AS DSPID,
    h.PageID AS PageID,
    PartnerShare
FROM $pages_hash AS h
INNER JOIN $pages_filtered_hash AS fh
ON (
    h.DSPID = fh.DSPID AND
    h.PageID = fh.PageID AND
    h.ImpCount = fh.ImpCount AND
    h.ImpHash = fh.ImpHash
);

$pages_consistent_turnover =
SELECT 
    p.DSPID AS DSPID,
    p.PageID AS PageID,
    p.PartnerShare AS PartnerShare,
    t.revenue AS revenue,
    t.revenue_w_cpa AS revenue_w_cpa,
    t.rtb_revenue AS rtb_revenue,
    t.rtb_tac AS rtb_tac,
    t.tac AS tac
FROM $pages_consistent AS p
LEFT JOIN (
    SELECT
        dspid, pageid,
        SUM(revenue) AS revenue,
        SUM(revenue_w_cpa) AS revenue_w_cpa,
        SUM(rtb_revenue) AS rtb_revenue,
        SUM(rtb_tac) AS rtb_tac,
        SUM(tac) AS tac,
    FROM $turnover_table
    GROUP BY dspid, pageid
) AS t ON (
    t.dspid = p.DSPID AND
    t.pageid = p.PageID
);

$page_imps =
SELECT
    pd.DSPID AS DSPID,
    pd.PageID AS PageID,
    pd.ImpID AS ImpID,
    pd.PartnerShare AS PartnerShare
FROM $page_dsp_filtered AS pd
LEFT ONLY JOIN $pages_consistent AS pc ON (
    pd.DSPID = pc.DSPID AND
    pd.PageID = pc.PageID
);

$page_imps_turnover =
SELECT 
    p.DSPID AS DSPID,
    p.PageID AS PageID,
    p.ImpID AS ImpID,
    p.PartnerShare AS PartnerShare,
    t.revenue AS revenue,
    t.revenue_w_cpa AS revenue_w_cpa,
    t.rtb_revenue AS rtb_revenue,
    t.rtb_tac AS rtb_tac,
    t.tac AS tac
FROM $page_imps AS p
LEFT JOIN $turnover_table AS t ON (
    t.dspid = p.DSPID AND
    t.pageid = p.PageID AND
    t.impid = p.ImpID
);

--- FIND SECONDARY IDs TO OVERWRITE

$secondary_page_imps =
SELECT 
    ps.DSPID AS DSPID,
    ps.PageID AS PageID,
    ps.ImpID AS ImpID,
    ps.PartnerShare AS PartnerShare,
    TRUE AS IsSecondary
FROM $page_partner_share_table AS ps
INNER JOIN $pages_consistent AS pc ON (
    ps.DSPID = pc.DSPID AND
    ps.PageID = pc.PageID
)
WHERE 
    ps.ImpID > 0 AND
    ps.PartnerShare>=$CurrentPartnerShareFrom AND
    ps.PartnerShare<=$CurrentPartnerShareTo
;

-- Secondary page_imps do not need separate turnover, because their turnover is already calculated at page level

$changes_1 =
SELECT 
    1 AS ChangesFilterId,
    0 AS PartnerID,
    DSPID ?? 0 AS DSPID,
    PageID ?? 0 AS PageID,
    ImpID ?? 0 AS ImpID,
    PartnerShare,
    revenue,
    revenue_w_cpa,
    rtb_revenue,
    rtb_tac,
    tac,
    $NewPartnerShare AS NewPartnerShare,
    $DeltaPartnerShare AS DeltaPartnerShare,
    IsSecondary
FROM (
    SELECT * FROM $pages_consistent_turnover
    UNION ALL
    SELECT * FROM $page_imps_turnover
    UNION ALL
    SELECT * FROM $secondary_page_imps
);



-- Concatenate filtered rows

$changes =
        SELECT * FROM $changes_1
;

-- Mark rows that are overwritten by next filter blocks

$max_filter_id =
SELECT 
    DSPID, PartnerID, PageID, ImpID,
    MAX(ChangesFilterId) AS MaxChangesFilterId
FROM $changes
GROUP BY DSPID, PartnerID, PageID, ImpID;

$PlannedPartnerShare = ($row) -> {
    RETURN MIN_OF(1000000, MAX_OF(0, IF(
        $row.NewPartnerShare IS NULL, 
        $row.PartnerShare + $row.DeltaPartnerShare, 
        $row.NewPartnerShare
    )))
};

$IsClamped = ($row) -> {
    $value = IF(
        $row.NewPartnerShare IS NULL,
        $row.PartnerShare + $row.DeltaPartnerShare,
        $row.NewPartnerShare
    );
    RETURN IF($value < 0, TRUE, IF($value > 1000000, TRUE, FALSE))
};

$marked_changes =
SELECT 
    c.ChangesFilterId AS ChangesFilterId,
    c.PartnerID AS PartnerID,
    c.DSPID AS DSPID,
    c.PageID AS PageID,
    c.ImpID AS ImpID,
    c.PartnerShare AS PartnerShare,
    c.NewPartnerShare AS NewPartnerShare,
    c.DeltaPartnerShare AS DeltaPartnerShare,
    c.revenue AS revenue,
    c.revenue_w_cpa AS revenue_w_cpa,
    c.rtb_revenue AS rtb_revenue,
    c.rtb_tac AS rtb_tac,
    c.tac AS tac,
    $PlannedPartnerShare(TableRow()) AS PlannedPartnerShare,
    IF(c.tac IS NULL, 0, $PlannedPartnerShare(TableRow()) * c.tac / 10000.0) AS PlannedPartnerPrice,
    $IsClamped(TableRow()) AS IsClamped,
    c.IsSecondary AS IsSecondary,
    IF(c.ChangesFilterId == m.MaxChangesFilterId, FALSE, TRUE) AS IsOverwrittenByNextFilter
FROM $changes AS c
LEFT JOIN $max_filter_id AS m
ON (
    c.DSPID == m.DSPID AND
    c.PartnerID == m.PartnerID AND
    c.PageID == m.PageID AND
    c.ImpID == m.ImpID
);

INSERT INTO `//home/yabs/tac-manager/request/test6/filter/changes` WITH TRUNCATE
SELECT * FROM $marked_changes;

INSERT INTO `//home/yabs/tac-manager/request/test6/filter/changes_stat` WITH TRUNCATE
SELECT
    ChangesFilterId,
    IsOverwrittenByNextFilter,
    IsSecondary,
    IsClamped,
    PageLevel,
    PartnerShare,
    COUNT(*) AS Rows,
    COUNT(DISTINCT PageID) AS Pages,
    COUNT(DISTINCT ImpID) AS Imps,
    SUM(revenue) AS revenue,
    SUM(revenue_w_cpa) AS revenue_w_cpa,
    SUM(rtb_revenue) AS rtb_revenue,
    SUM(rtb_tac) AS rtb_tac,
    SUM(tac) AS tac,
FROM $marked_changes
GROUP BY 
    ChangesFilterId,
    IsOverwrittenByNextFilter,
    IsSecondary,
    IsClamped,
    PartnerShare,
    (ImpID==0) AS PageLevel
;

INSERT INTO `//home/yabs/tac-manager/request/test6/filter/changes_target` WITH TRUNCATE
SELECT
    PlannedPartnerShare,
    COUNT(*) AS Rows,
    COUNT(DISTINCT PageID) AS Pages,
    COUNT(DISTINCT ImpID) AS Imps,
    SUM(revenue) AS revenue,
    SUM(revenue_w_cpa) AS revenue_w_cpa,
    SUM(rtb_revenue) AS rtb_revenue,
    SUM(rtb_tac) AS rtb_tac,
    SUM(tac) AS tac,
FROM $marked_changes
GROUP BY 
    PlannedPartnerShare
;