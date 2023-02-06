
$yanTupleToStruct = ($t) -> {
    return AsStruct(
        $t.0 as YAN_AdSessionID,
        $t.1 as YAN_URL,
        $t.2 as YAN_AdType,
        $t.3 as YAN_AdbEnabled,
        $t.4 as YAN_BlockHeight,
        $t.5 as YAN_BlockWidth,
        $t.6 as YAN_DSPID,
        $t.7 as YAN_ImpID,
        $t.8 as YAN_IsRender,
        $t.9 as YAN_IsRequest,
        $t.10 as YAN_IsShow,
        $t.11 as YAN_PageID,
        $t.12 as YAN_PartnerPrice
    );
};

$yan = ($row) -> {
    return ListMap(ListSort(ListZip(
        $row.YAN_AdSessionID,
        $row.YAN_URL,
        $row.YAN_AdType,
        $row.YAN_AdbEnabled,
        $row.YAN_BlockHeight,
        $row.YAN_BlockWidth,
        $row.YAN_DSPID,
        $row.YAN_ImpID,
        $row.YAN_IsRender,
        $row.YAN_IsRequest,
        $row.YAN_IsShow,
        $row.YAN_PageID,
        $row.YAN_PartnerPrice
    )), $yanTupleToStruct);
};

$adfoxTupleToStruct = ($t) -> {
    return AsStruct(
        $t.0 as Adfox_AdSessionID,
        $t.1 as Adfox_URL,
        $t.2 as Adfox_RequestSession,
        $t.3 as Adfox_WinPriority,
        $t.4 as Adfox_RtbAuctionScheduleStepIndex,
        $t.5 as Adfox_OwnerID,
        $t.6 as Adfox_BannerID,
        $t.7 as Adfox_BannerTypeID,
        $t.8 as Adfox_CampaignID,
        $t.9 as Adfox_CampaignKindID,
        $t.10 as Adfox_MonetizationTypeID,
        $t.11 as Adfox_SystemType,
        $t.12 as Adfox_Price,
        $t.13 as Adfox_Level1,
        $t.14 as Adfox_Level2,
        $t.15 as Adfox_SiteID,
        $t.16 as Adfox_SectionID,
        $t.17 as Adfox_PlaceID,
        $t.18 as Adfox_YanPageID,
        $t.19 as Adfox_YanImpID,
        $t.20 as Adfox_Load,
        $t.21 as Adfox_View,
        $t.22 as Adfox_Click,
        $t.23 as Adfox_GoogleSlotGroupID,
        $t.24 as Adfox_EventID,
        $t.25 as Adfox_PuidKey,
        $t.26 as Adfox_PuidVal
    );
};

$adfoxPuidTupleToStruct = ($t) -> {
    return AsStruct(
        $t.0 as Adfox_PuidKey,
        $t.1 as Adfox_PuidVal
    );
};

$adfoxPuid = ($row) -> {
    return ListMap(ListSort(ListZip(
        $row.Adfox_PuidKey,
        $row.Adfox_PuidVal
    )), $adfoxPuidTupleToStruct);
};

$adfox = ($row) -> {
    return ListMap(
        ListMap(ListSort(ListZip(
            $row.Adfox_AdSessionID,
            $row.Adfox_URL,
            $row.Adfox_RequestSession,
            $row.Adfox_WinPriority,
            $row.Adfox_RtbAuctionScheduleStepIndex,
            $row.Adfox_OwnerID,
            $row.Adfox_BannerID,
            $row.Adfox_BannerTypeID,
            $row.Adfox_CampaignID,
            $row.Adfox_CampaignKindID,
            $row.Adfox_MonetizationTypeID,
            $row.Adfox_SystemType,
            $row.Adfox_Price,
            $row.Adfox_Level1,
            $row.Adfox_Level2,
            $row.Adfox_SiteID,
            $row.Adfox_SectionID,
            $row.Adfox_PlaceID,
            $row.Adfox_YanPageID,
            $row.Adfox_YanImpID,
            $row.Adfox_Load,
            $row.Adfox_View,
            $row.Adfox_Click,
            $row.Adfox_GoogleSlotGroupID,
            $row.Adfox_EventID,
            $row.Adfox_PuidKey,
            $row.Adfox_PuidVal
        )), $adfoxTupleToStruct),
        ($x) -> {
            return CombineMembers(
                RemoveMembers($x, [
                    "Adfox_EventID",
                    "Adfox_PuidKey",
                    "Adfox_PuidVal"
                ]),
                AsStruct(
                    ListSort($x.Adfox_EventID) as Adfox_EventID,
                    ListExtract($adfoxPuid($x), "Adfox_PuidKey") as Adfox_PuidKey,
                    ListExtract($adfoxPuid($x), "Adfox_PuidVal") as Adfox_PuidVal
                )
            );
        }
    );
};

$rwTupleToStruct = ($t) -> {
    return AsStruct(
        $t.0 as RecommendationWidget_BidReqID,
        $t.1 as RecommendationWidget_AdSessionID,
        $t.2 as RecommendationWidget_Action,
        $t.3 as RecommendationWidget_PageID,
        $t.4 as RecommendationWidget_URL,
        $t.5 as RecommendationWidget_Position,
        $t.6 as RecommendationWidget_ArticleURL
    );
};

$rwMaterialToStruct = ($t) -> {
    return AsStruct(
        $t.0 as RecommendationWidget_Action,
        $t.1 as RecommendationWidget_URL,
        $t.2 as RecommendationWidget_Position,
        $t.3 as RecommendationWidget_ArticleURL
    );
};

$rwMaterial = ($row) -> {
    return ListMap(ListSort(ListZip(
        $row.RecommendationWidget_Action,
        $row.RecommendationWidget_URL,
        $row.RecommendationWidget_Position,
        $row.RecommendationWidget_ArticleURL
    )), $rwMaterialToStruct);
};

$rw = ($row) -> {
    return ListMap(
        ListMap(ListSort(ListZip(
            $row.RecommendationWidget_BidReqID,
            $row.RecommendationWidget_AdSessionID,
            $row.RecommendationWidget_Action,
            $row.RecommendationWidget_PageID,
            $row.RecommendationWidget_URL,
            $row.RecommendationWidget_Position,
            $row.RecommendationWidget_ArticleURL
        )), $rwTupleToStruct),
        ($x) -> {
            return CombineMembers(
                RemoveMembers($x, [
                    "RecommendationWidget_Action",
                    "RecommendationWidget_URL",
                    "RecommendationWidget_Position",
                    "RecommendationWidget_ArticleURL"
                ]),
                AsStruct(
                    ListExtract($rwMaterial($x), "RecommendationWidget_Action") as RecommendationWidget_Action,
                    ListExtract($rwMaterial($x), "RecommendationWidget_URL") as RecommendationWidget_URL,
                    ListExtract($rwMaterial($x), "RecommendationWidget_Position") as RecommendationWidget_Position,
                    ListExtract($rwMaterial($x), "RecommendationWidget_ArticleURL") as RecommendationWidget_ArticleURL
                )
            );
        }
    );
};

insert into `${destinationTable}`
select
    ListExtract($yan(TableRow()), "YAN_AdSessionID") as YAN_AdSessionID,
    ListExtract($yan(TableRow()), "YAN_URL") as YAN_URL,
    ListExtract($yan(TableRow()), "YAN_AdType") as YAN_AdType,
    ListExtract($yan(TableRow()), "YAN_AdbEnabled") as YAN_AdbEnabled,
    ListExtract($yan(TableRow()), "YAN_BlockHeight") as YAN_BlockHeight,
    ListExtract($yan(TableRow()), "YAN_BlockWidth") as YAN_BlockWidth,
    ListExtract($yan(TableRow()), "YAN_DSPID") as YAN_DSPID,
    ListExtract($yan(TableRow()), "YAN_ImpID") as YAN_ImpID,
    ListExtract($yan(TableRow()), "YAN_IsRender") as YAN_IsRender,
    ListExtract($yan(TableRow()), "YAN_IsRequest") as YAN_IsRequest,
    ListExtract($yan(TableRow()), "YAN_IsShow") as YAN_IsShow,
    ListExtract($yan(TableRow()), "YAN_PageID") as YAN_PageID,
    ListExtract($yan(TableRow()), "YAN_PartnerPrice") as YAN_PartnerPrice,

    ListExtract($adfox(TableRow()), "Adfox_AdSessionID") as Adfox_AdSessionID,
    ListExtract($adfox(TableRow()), "Adfox_URL") as Adfox_URL,
    ListExtract($adfox(TableRow()), "Adfox_RequestSession") as Adfox_RequestSession,
    ListExtract($adfox(TableRow()), "Adfox_WinPriority") as Adfox_WinPriority,
    ListExtract($adfox(TableRow()), "Adfox_RtbAuctionScheduleStepIndex") as Adfox_RtbAuctionScheduleStepIndex,
    ListExtract($adfox(TableRow()), "Adfox_OwnerID") as Adfox_OwnerID,
    ListExtract($adfox(TableRow()), "Adfox_BannerID") as Adfox_BannerID,
    ListExtract($adfox(TableRow()), "Adfox_BannerTypeID") as Adfox_BannerTypeID,
    ListExtract($adfox(TableRow()), "Adfox_CampaignID") as Adfox_CampaignID,
    ListExtract($adfox(TableRow()), "Adfox_CampaignKindID") as Adfox_CampaignKindID,
    ListExtract($adfox(TableRow()), "Adfox_MonetizationTypeID") as Adfox_MonetizationTypeID,
    ListExtract($adfox(TableRow()), "Adfox_SystemType") as Adfox_SystemType,
    ListExtract($adfox(TableRow()), "Adfox_Price") as Adfox_Price,
    ListExtract($adfox(TableRow()), "Adfox_Level1") as Adfox_Level1,
    ListExtract($adfox(TableRow()), "Adfox_Level2") as Adfox_Level2,
    ListExtract($adfox(TableRow()), "Adfox_SiteID") as Adfox_SiteID,
    ListExtract($adfox(TableRow()), "Adfox_SectionID") as Adfox_SectionID,
    ListExtract($adfox(TableRow()), "Adfox_PlaceID") as Adfox_PlaceID,
    ListExtract($adfox(TableRow()), "Adfox_YanPageID") as Adfox_YanPageID,
    ListExtract($adfox(TableRow()), "Adfox_YanImpID") as Adfox_YanImpID,
    ListExtract($adfox(TableRow()), "Adfox_Load") as Adfox_Load,
    ListExtract($adfox(TableRow()), "Adfox_View") as Adfox_View,
    ListExtract($adfox(TableRow()), "Adfox_Click") as Adfox_Click,
    ListExtract($adfox(TableRow()), "Adfox_GoogleSlotGroupID") as Adfox_GoogleSlotGroupID,
    ListExtract($adfox(TableRow()), "Adfox_EventID") as Adfox_EventID,
    ListExtract($adfox(TableRow()), "Adfox_PuidKey") as Adfox_PuidKey,
    ListExtract($adfox(TableRow()), "Adfox_PuidVal") as Adfox_PuidVal,

    ListExtract($rw(TableRow()), "RecommendationWidget_BidReqID") as RecommendationWidget_BidReqID,
    ListExtract($rw(TableRow()), "RecommendationWidget_AdSessionID") as RecommendationWidget_AdSessionID,
    ListExtract($rw(TableRow()), "RecommendationWidget_Action") as RecommendationWidget_Action,
    ListExtract($rw(TableRow()), "RecommendationWidget_PageID") as RecommendationWidget_PageID,
    ListExtract($rw(TableRow()), "RecommendationWidget_URL") as RecommendationWidget_URL,
    ListExtract($rw(TableRow()), "RecommendationWidget_Position") as RecommendationWidget_Position,
    ListExtract($rw(TableRow()), "RecommendationWidget_ArticleURL") as  RecommendationWidget_ArticleURL,

    t.* without
        YAN_AdSessionID,
        YAN_URL,
        YAN_AdType,
        YAN_AdbEnabled,
        YAN_BlockHeight,
        YAN_BlockWidth,
        YAN_DSPID,
        YAN_ImpID,
        YAN_IsRender,
        YAN_IsRequest,
        YAN_IsShow,
        YAN_PageID,
        YAN_PartnerPrice,

        Adfox_AdSessionID,
        Adfox_URL,
        Adfox_RequestSession,
        Adfox_WinPriority,
        Adfox_RtbAuctionScheduleStepIndex,
        Adfox_OwnerID,
        Adfox_BannerID,
        Adfox_BannerTypeID,
        Adfox_CampaignID,
        Adfox_CampaignKindID,
        Adfox_MonetizationTypeID,
        Adfox_SystemType,
        Adfox_Price,
        Adfox_Level1,
        Adfox_Level2,
        Adfox_SiteID,
        Adfox_SectionID,
        Adfox_PlaceID,
        Adfox_YanPageID,
        Adfox_YanImpID,
        Adfox_Load,
        Adfox_View,
        Adfox_Click,
        Adfox_GoogleSlotGroupID,
        Adfox_EventID,
        Adfox_PuidKey,
        Adfox_PuidVal,

        RecommendationWidget_BidReqID,
        RecommendationWidget_AdSessionID,
        RecommendationWidget_Action,
        RecommendationWidget_PageID,
        RecommendationWidget_URL,
        RecommendationWidget_Position,
        RecommendationWidget_ArticleURL

from concat(
<#list sourceTables as t>
    `${t}`<#sep>,</#sep>
</#list>
) as t
order by <#list groupColumns as c>${c}<#sep>, </#sep></#list> desc
