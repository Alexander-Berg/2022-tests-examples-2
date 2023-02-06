USE chyt.hahn/lelby_ckique;
pragma chyt.dynamic_table.enable_dynamic_store_read = 0;
pragma chyt.execution.join_policy=local;

INSERT INTO "<append=%false>//home/yabs/tac-manager/request/test6/filter/changes_imps"

WITH $changes AS (
    SELECT *
    FROM (
        SELECT
            DSPID,
            pd.PageID AS PageID,
            pd.ImpID AS ImpID,
            PartnerShare,
            1 AS ChangesFilterId,
            PartnerID,
            null AS NewPartnerShare,
            20000 AS DeltaPartnerShare,
            LEAST(1000000, GREATEST(0, PartnerShare + DeltaPartnerShare)) AS PlannedPartnerShare,
            IF (PartnerShare + DeltaPartnerShare < 0, 1, IF (PartnerShare + DeltaPartnerShare > 1000000, 1, 0)) AS IsClamped,
            rtb_revenue as rtb_revenue,
            rtb_tac as rtb_tac,
            revenue as revenue,
            tac as tac,
            IF(rtb_revenue IS null, 0, PlannedPartnerShare * rtb_revenue / 1000000.0) AS PlannedPartnerPrice,
            segment AS Segment,
            traffic_type AS TrafficType,
            Domain,
            Login,
            bitTest(pi.Options, 7) OR bitTest(pi.Options, 16) AS IsTurboOrTurboDesktop
        FROM `//home/yabs-cs/key_1/v2/export/CaesarPage/PageDSP.last` AS pd
        LEFT SEMI JOIN (
            SELECT page_id, block_id, segment, traffic_type
            FROM `//home/comdep-analytics/YAN/segmentation/static/latest/blocks`
            WHERE
        segment not in ('tier-1','tier-0') AND
        traffic_type in ('type1','type2')
        ) AS s ON
            s.page_id = toUInt64(pd.PageID) AND
            s.block_id = toUInt64(pd.ImpID)
        LEFT SEMI JOIN (
            SELECT PageID, Login, splitByString(',', COALESCE(DomainList, ''))[1] AS Domain, PartnerID
            FROM `//home/yabs/dict/PartnerPage`
            WHERE
        Login not in ('aark','okwedook') AND
        splitByString(',', COALESCE(DomainList, ''))[1] in ('yandex.ru','ya.ru') AND
        PartnerID in (22,33,44)
        ) AS pp ON
            pd.PageID = pp.PageID
        LEFT SEMI JOIN (
            SELECT PageID, (OptionsYandexApp or OptionsYandexGroup or OptionsYandexPage) AS IsInternal
            FROM `//home/yabs/dict/Page`
            WHERE
        (OptionsYandexApp or OptionsYandexGroup or OptionsYandexPage) in (1)
        ) AS p ON
            pd.PageID = p.PageID
        LEFT JOIN `//home/yabs/tac-manager/turnover/last` AS t ON
            t.dspid = pd.DSPID AND
            t.pageid = toUInt64(pd.PageID) AND
            t.impid = toUInt64(pd.ImpID)
        LEFT JOIN `//home/yabs-cs/export/PageImp` AS pi ON
            pi.PageID = pd.PageID AND
            pi.ImpID = pd.ImpID
        WHERE
        DSPID not in (5,6) AND
        PageID not in (414314,414314) AND
        (PageID,ImpID) not in ((1,2),(3,4),(5,6)) AND
        DSPID not in (5,10) AND
        PartnerShare >= 10000 AND PartnerShare <= 900000
        UNION ALL
        SELECT
            DSPID,
            pd.PageID AS PageID,
            pd.ImpID AS ImpID,
            PartnerShare,
            2 AS ChangesFilterId,
            PartnerID,
            400000 AS NewPartnerShare,
            null AS DeltaPartnerShare,
            LEAST(1000000, GREATEST(0, NewPartnerShare)) AS PlannedPartnerShare,
            IF (NewPartnerShare < 0, 1, IF (NewPartnerShare > 1000000, 1, 0)) AS IsClamped,
            rtb_revenue as rtb_revenue,
            rtb_tac as rtb_tac,
            revenue as revenue,
            tac as tac,
            IF(rtb_revenue IS null, 0, PlannedPartnerShare * rtb_revenue / 1000000.0) AS PlannedPartnerPrice,
            segment AS Segment,
            traffic_type AS TrafficType,
            Domain,
            Login,
            bitTest(pi.Options, 7) OR bitTest(pi.Options, 16) AS IsTurboOrTurboDesktop
        FROM `//home/yabs-cs/key_1/v2/export/CaesarPage/PageDSP.last` AS pd
        LEFT SEMI JOIN (
            SELECT page_id, block_id, segment, traffic_type
            FROM `//home/comdep-analytics/YAN/segmentation/static/latest/blocks`
            WHERE
        segment in ('tier-1','tier-0')
        ) AS s ON
            s.page_id = toUInt64(pd.PageID) AND
            s.block_id = toUInt64(pd.ImpID)
        LEFT SEMI JOIN (
            SELECT PageID, Login, splitByString(',', COALESCE(DomainList, ''))[1] AS Domain, PartnerID
            FROM `//home/yabs/dict/PartnerPage`
            WHERE
        Login in ('aark','okwedook')
        ) AS pp ON
            pd.PageID = pp.PageID
        LEFT SEMI JOIN (
            SELECT PageID, (OptionsYandexApp or OptionsYandexGroup or OptionsYandexPage) AS IsInternal
            FROM `//home/yabs/dict/Page`
        ) AS p ON
            pd.PageID = p.PageID
        LEFT JOIN `//home/yabs/tac-manager/turnover/last` AS t ON
            t.dspid = pd.DSPID AND
            t.pageid = toUInt64(pd.PageID) AND
            t.impid = toUInt64(pd.ImpID)
        LEFT JOIN `//home/yabs-cs/export/PageImp` AS pi ON
            pi.PageID = pd.PageID AND
            pi.ImpID = pd.ImpID
        WHERE
        DSPID in (5,6) AND
        (PageID,ImpID) in ((1,2),(3,4),(5,6)) AND
        PageID in (1234) AND
        DSPID not in (5,10) AND
        PartnerShare >= 20000 AND PartnerShare <= 800000
    )
)

SELECT
    c.*,
    IF(c.ChangesFilterId == m.MaxChangesFilterId, 0, 1) AS IsOverwrittenByNextFilter
FROM (
    SELECT * FROM $changes
    WHERE PlannedPartnerShare <= 1000000
) AS c
LEFT JOIN (
    SELECT 
        DSPID, PartnerID, PageID, ImpID,
        MAX(ChangesFilterId) AS MaxChangesFilterId
    FROM $changes
    GROUP BY DSPID, PartnerID, PageID, ImpID
) AS m ON 
    c.DSPID = m.DSPID AND
    c.PartnerID = m.PartnerID AND
    c.PageID = m.PageID AND
    c.ImpID = m.ImpID
;

INSERT INTO "<append=%false>//home/yabs/tac-manager/request/test6/filter/changes_stat"
SELECT
    COUNT(*) AS Rows,
    COUNT(DISTINCT PageID) AS Pages,
    COUNT(DISTINCT PageID, ImpID) AS Imps,
    SUM(IsClamped) AS Clamps,
    SUM(IsOverwrittenByNextFilter) AS Overwrites,
    SUM(rtb_revenue * IF(IsOverwrittenByNextFilter, 0, 1)) AS TurnoverRtb,
    SUM(revenue * IF(IsOverwrittenByNextFilter, 0, 1)) AS Turnover,
    SUM(tac * IF(IsOverwrittenByNextFilter, 0, 1)) AS PartnerPrice,
    SUM(rtb_tac * IF(IsOverwrittenByNextFilter, 0, 1)) AS PartnerPriceRtb,
    SUM(PlannedPartnerPrice * IF(IsOverwrittenByNextFilter, 0, 1)) AS PlannedPartnerPrice,
    '//home/yabs/tac-manager/turnover/last' AS TurnoverSourceTable
FROM `//home/yabs/tac-manager/request/test6/filter/changes_imps`
;