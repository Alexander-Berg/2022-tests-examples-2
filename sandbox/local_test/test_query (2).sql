USE chyt.hahn/lelby_ckique;
pragma chyt.dynamic_table.enable_dynamic_store_read = 0;
pragma chyt.execution.join_policy=local;

INSERT INTO "<append=%false>//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_touched1"
SELECT
    DSPID,
    pd.PageID AS PageID,
    ImpID,
    PartnerShare
FROM `//home/yabs-cs/key_1/v2/export/CaesarPage/PageDSP.last` AS pd
LEFT SEMI JOIN (
    SELECT DISTINCT page_id
    FROM `//home/comdep-analytics/YAN/segmentation/static/latest/blocks`
    WHERE 
        segment not in ('tier-1','tier-0') AND
        traffic_type in ('type1','type2')
) AS s ON
    s.page_id = toUInt64(pd.PageID)
LEFT SEMI JOIN (
    SELECT PageID
    FROM `//home/yabs/dict/PartnerPage`
    WHERE 
        Login not in ('aark','okwedook') AND
        splitByString(',', COALESCE(DomainList, ''))[1] in ('yandex.ru','ya.ru') AND
        PartnerID in (22,33,44)
) AS pp ON
    pd.PageID = pp.PageID
LEFT SEMI JOIN (
    SELECT PageID
    FROM `//home/yabs/dict/Page`
    WHERE 
        (OptionsYandexApp or OptionsYandexGroup or OptionsYandexPage) in (1)
) AS p ON
    pd.PageID = p.PageID
WHERE 
    DSPID not in (5,10) AND
        DSPID not in (5,6) AND
        PageID not in (414314,414314)
;

INSERT INTO "<append=%false>//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/page_dsp_filtered1"
    SELECT
        pd.DSPID AS DSPID,
        pd.PageID AS PageID,
        pd.ImpID AS ImpID,
        pd.PartnerShare AS PartnerShare
    FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_touched1` AS pd
    LEFT SEMI JOIN (
        SELECT page_id, block_id 
        FROM `//home/comdep-analytics/YAN/segmentation/static/latest/blocks`
        WHERE
        segment not in ('tier-1','tier-0') AND
        traffic_type in ('type1','type2')
    ) AS s ON
        s.page_id = toUInt64(pd.PageID) AND
        s.block_id = toUInt64(pd.ImpID)
    LEFT SEMI JOIN (
        SELECT PageID
        FROM `//home/yabs/dict/PartnerPage`
        WHERE
        Login not in ('aark','okwedook') AND
        splitByString(',', COALESCE(DomainList, ''))[1] in ('yandex.ru','ya.ru') AND
        PartnerID in (22,33,44)
    ) AS pp ON
        pd.PageID = toUInt64(pp.PageID)
    WHERE 
        DSPID not in (5,6) AND
        PageID not in (414314,414314) AND
        PartnerShare >= 10000 AND PartnerShare <= 900000
;

INSERT INTO "<append=%false>//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_consistent1"

WITH $pages_hash AS (
    SELECT
        DSPID,
        PageID,
        COUNT(*) AS ImpCount
    FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_touched1` AS pd
    GROUP BY DSPID, PageID

    HAVING COUNT(DISTINCT PartnerShare)=1
)

SELECT
    fh.DSPID AS DSPID,
    fh.PageID AS PageID,
    0 AS ImpID,
    MaxPartnerShare AS PartnerShare,
    IsTurboOrTurboDesktop
FROM (
    SELECT
        DSPID,
        PageID,
        MAX(PartnerShare) AS MaxPartnerShare,
        MAX(IsTurboOrTurboDesktop) AS IsTurboOrTurboDesktop,
        COUNT(*) AS ImpCount
    FROM (
        SELECT
            pd.*,
            bitTest(pi.Options, 7) OR bitTest(pi.Options, 16) AS IsTurboOrTurboDesktop
        FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/page_dsp_filtered1` AS pd
        LEFT SEMI JOIN `//home/yabs-cs/export/PageImp` AS pi ON
            toUInt64(pi.PageID) = pd.PageID AND
            toUInt64(pi.ImpID) = pd.ImpID
    )
    GROUP BY DSPID, PageID

    HAVING COUNT(DISTINCT PartnerShare)=1
) AS fh -- filtered hash
LEFT SEMI JOIN $pages_hash AS h ON -- hash
    h.DSPID = fh.DSPID AND
    h.PageID = fh.PageID AND
    h.ImpCount = fh.ImpCount
;

INSERT INTO "<append=%false>//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/changes1"

WITH $secondary_page_imps AS (
    SELECT 
        toUInt64(ps.DSPID) AS DSPID,
        toUInt64(ps.PageID) AS PageID,
        toUInt64(ps.ImpID) AS ImpID,
        toUInt64(ps.PartnerShare) AS PartnerShare
    FROM `//home/yabs/dict/PagePartnerShare` AS ps
    INNER JOIN (
        SELECT *
        FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_consistent1`
        -- Do not duplicate turbo imps in secondary rows, because if we could collapse turbo imps, this means that all imps are already overridden
        WHERE IsTurboOrTurboDesktop == 0
    ) AS pc ON
        toUInt64(ps.DSPID) = pc.DSPID AND
        toUInt64(ps.PageID) = pc.PageID
    WHERE 
        ps.ImpID > 0 AND
        ps.PartnerShare>=0 AND
        ps.PartnerShare<=1000000
),
$page_imps AS (
    SELECT
        toUInt64(f.DSPID) AS DSPID,
        toUInt64(f.PageID) AS PageID,
        toUInt64(f.ImpID) AS ImpID,
        toUInt64(f.PartnerShare) AS PartnerShare
    FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/page_dsp_filtered1` AS f
    LEFT ANTI JOIN (
        SELECT *
        FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_consistent1`
        -- This oneshot should contain rows both for (Pages with turbo imps) and (turbo imps) due to turbo priority
        WHERE IsTurboOrTurboDesktop == 0
    ) AS a ON
        a.DSPID = f.DSPID AND
        a.PageID = f.PageID
)

SELECT
    *,
    1 AS ChangesFilterId,
    0 AS PartnerID,
    null AS NewPartnerShare,
    20000 AS DeltaPartnerShare,
    LEAST(1000000, GREATEST(0, PartnerShare + DeltaPartnerShare)) AS PlannedPartnerShare
FROM (
    SELECT DSPID, PageID, ImpID, PartnerShare, 0 AS IsSecondary
    FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_consistent1`

    UNION ALL

    SELECT *, 0 AS IsSecondary
    FROM $page_imps

    UNION ALL

    SELECT *, 1 AS IsSecondary
    FROM $secondary_page_imps
);

INSERT INTO "<append=%false>//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_touched2"
SELECT
    DSPID,
    pd.PageID AS PageID,
    ImpID,
    PartnerShare
FROM `//home/yabs-cs/key_1/v2/export/CaesarPage/PageDSP.last` AS pd
LEFT SEMI JOIN (
    SELECT DISTINCT page_id
    FROM `//home/comdep-analytics/YAN/segmentation/static/latest/blocks`
    WHERE 
        segment in ('tier-1','tier-0')
) AS s ON
    s.page_id = toUInt64(pd.PageID)
LEFT SEMI JOIN (
    SELECT PageID
    FROM `//home/yabs/dict/PartnerPage`
    WHERE 
        Login in ('aark','okwedook')
) AS pp ON
    pd.PageID = pp.PageID
WHERE 
    DSPID not in (5,10) AND
        DSPID in (5,6) AND
        PageID in (1234)
;

INSERT INTO "<append=%false>//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/page_dsp_filtered2"
    SELECT
        pd.DSPID AS DSPID,
        pd.PageID AS PageID,
        pd.ImpID AS ImpID,
        pd.PartnerShare AS PartnerShare
    FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_touched2` AS pd
    LEFT SEMI JOIN (
        SELECT page_id, block_id 
        FROM `//home/comdep-analytics/YAN/segmentation/static/latest/blocks`
        WHERE
        segment in ('tier-1','tier-0')
    ) AS s ON
        s.page_id = toUInt64(pd.PageID) AND
        s.block_id = toUInt64(pd.ImpID)
    LEFT SEMI JOIN (
        SELECT PageID
        FROM `//home/yabs/dict/PartnerPage`
        WHERE
        Login in ('aark','okwedook')
    ) AS pp ON
        pd.PageID = toUInt64(pp.PageID)
    WHERE 
        DSPID in (5,6) AND
        PageID in (1234) AND
        PartnerShare >= 20000 AND PartnerShare <= 800000
;

INSERT INTO "<append=%false>//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_consistent2"

WITH $pages_hash AS (
    SELECT
        DSPID,
        PageID,
        COUNT(*) AS ImpCount
    FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_touched2` AS pd
    GROUP BY DSPID, PageID

)

SELECT
    fh.DSPID AS DSPID,
    fh.PageID AS PageID,
    0 AS ImpID,
    MaxPartnerShare AS PartnerShare,
    IsTurboOrTurboDesktop
FROM (
    SELECT
        DSPID,
        PageID,
        MAX(PartnerShare) AS MaxPartnerShare,
        MAX(IsTurboOrTurboDesktop) AS IsTurboOrTurboDesktop,
        COUNT(*) AS ImpCount
    FROM (
        SELECT
            pd.*,
            bitTest(pi.Options, 7) OR bitTest(pi.Options, 16) AS IsTurboOrTurboDesktop
        FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/page_dsp_filtered2` AS pd
        LEFT SEMI JOIN `//home/yabs-cs/export/PageImp` AS pi ON
            toUInt64(pi.PageID) = pd.PageID AND
            toUInt64(pi.ImpID) = pd.ImpID
    )
    GROUP BY DSPID, PageID

) AS fh -- filtered hash
LEFT SEMI JOIN $pages_hash AS h ON -- hash
    h.DSPID = fh.DSPID AND
    h.PageID = fh.PageID AND
    h.ImpCount = fh.ImpCount
;

INSERT INTO "<append=%false>//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/changes2"

WITH $secondary_page_imps AS (
    SELECT 
        toUInt64(ps.DSPID) AS DSPID,
        toUInt64(ps.PageID) AS PageID,
        toUInt64(ps.ImpID) AS ImpID,
        toUInt64(ps.PartnerShare) AS PartnerShare
    FROM `//home/yabs/dict/PagePartnerShare` AS ps
    INNER JOIN (
        SELECT *
        FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_consistent2`
        -- Do not duplicate turbo imps in secondary rows, because if we could collapse turbo imps, this means that all imps are already overridden
        WHERE IsTurboOrTurboDesktop == 0
    ) AS pc ON
        toUInt64(ps.DSPID) = pc.DSPID AND
        toUInt64(ps.PageID) = pc.PageID
    WHERE 
        ps.ImpID > 0 AND
        ps.PartnerShare>=0 AND
        ps.PartnerShare<=1000000
),
$page_imps AS (
    SELECT
        toUInt64(f.DSPID) AS DSPID,
        toUInt64(f.PageID) AS PageID,
        toUInt64(f.ImpID) AS ImpID,
        toUInt64(f.PartnerShare) AS PartnerShare
    FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/page_dsp_filtered2` AS f
    LEFT ANTI JOIN (
        SELECT *
        FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_consistent2`
        -- This oneshot should contain rows both for (Pages with turbo imps) and (turbo imps) due to turbo priority
        WHERE IsTurboOrTurboDesktop == 0
    ) AS a ON
        a.DSPID = f.DSPID AND
        a.PageID = f.PageID
)

SELECT
    *,
    2 AS ChangesFilterId,
    0 AS PartnerID,
    400000 AS NewPartnerShare,
    null AS DeltaPartnerShare,
    LEAST(1000000, GREATEST(0, NewPartnerShare)) AS PlannedPartnerShare
FROM (
    SELECT DSPID, PageID, ImpID, PartnerShare, 0 AS IsSecondary
    FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/pages_consistent2`

    UNION ALL

    SELECT *, 0 AS IsSecondary
    FROM $page_imps

    UNION ALL

    SELECT *, 1 AS IsSecondary
    FROM $secondary_page_imps
);



INSERT INTO "<append=%false>//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/changes"

WITH $changes AS (
    SELECT *
    FROM (
        SELECT * FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/changes1`
        UNION ALL
        SELECT * FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/tmp/changes2`
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

INSERT INTO "<append=%false>//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/changes_target"
SELECT
    PlannedPartnerShare,
    COUNT(*) AS Rows
FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/changes`
GROUP BY 
    PlannedPartnerShare
;

INSERT INTO `<append=%false>//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/changes_uneq`
SELECT
    c.*,
    p.PlannedPartnerShare AS PrevPlannedPartnerShare
FROM `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/changes` AS c
INNER JOIN `//home/yabs/tac-manager/request/TESTTACCHANGES-21/filter/changes` AS p ON (
    c.DSPID = p.DSPID AND
    c.PartnerID = p.PartnerID AND
    c.PageID = p.PageID AND
    c.ImpID = p.ImpID
)
WHERE
    c.PlannedPartnerShare != p.PlannedPartnerShare
;