package ru.yandex.autotests.metrika.tests.ft.management.logsapi;

public class LogsApiTestData {

    public static final String VISITS_FIELDS = "ym:s:visitID,ym:s:counterID,ym:s:watchIDs,ym:s:date," +
            "ym:s:dateTime,ym:s:dateTimeUTC,ym:s:isNewUser,ym:s:startURL,ym:s:endURL,ym:s:pageViews," +
            "ym:s:visitDuration,ym:s:bounce,ym:s:ipAddress,ym:s:regionCountry,ym:s:regionCity," +
            "ym:s:regionCountryID,ym:s:regionCityID,ym:s:clientID,ym:s:networkType,ym:s:goalsID," +
            "ym:s:goalsSerialNumber,ym:s:goalsDateTime,ym:s:goalsPrice,ym:s:goalsOrder,ym:s:goalsCurrency," +
            "ym:s:lastTrafficSource,ym:s:lastAdvEngine,ym:s:lastReferalSource,ym:s:lastSearchEngineRoot," +
            "ym:s:lastSearchEngine,ym:s:lastSocialNetwork,ym:s:lastSocialNetworkProfile,ym:s:referer," +
            "ym:s:lastDirectClickOrder,ym:s:lastDirectBannerGroup,ym:s:lastDirectClickBanner," +
            "ym:s:lastDirectClickOrderName,ym:s:lastClickBannerGroupName,ym:s:lastDirectClickBannerName," +
            "ym:s:lastDirectPhraseOrCond,ym:s:lastDirectPlatformType,ym:s:lastDirectPlatform," +
            "ym:s:lastDirectConditionType,ym:s:lastCurrencyID,ym:s:from,ym:s:UTMCampaign,ym:s:UTMContent," +
            "ym:s:UTMMedium,ym:s:UTMSource,ym:s:UTMTerm,ym:s:openstatAd,ym:s:openstatCampaign," +
            "ym:s:openstatService,ym:s:openstatSource,ym:s:hasGCLID,ym:s:lastGCLID,ym:s:firstGCLID," +
            "ym:s:lastSignificantGCLID,ym:s:browserLanguage,ym:s:browserCountry,ym:s:clientTimeZone," +
            "ym:s:deviceCategory,ym:s:mobilePhone,ym:s:mobilePhoneModel,ym:s:operatingSystemRoot," +
            "ym:s:operatingSystem,ym:s:browser,ym:s:browserMajorVersion,ym:s:browserMinorVersion," +
            "ym:s:browserEngine,ym:s:browserEngineVersion1,ym:s:browserEngineVersion2," +
            "ym:s:browserEngineVersion3,ym:s:browserEngineVersion4,ym:s:cookieEnabled,ym:s:javascriptEnabled," +
            "ym:s:screenFormat,ym:s:screenColors,ym:s:screenOrientation,ym:s:screenWidth,ym:s:screenHeight," +
            "ym:s:physicalScreenWidth,ym:s:physicalScreenHeight,ym:s:windowClientWidth,ym:s:windowClientHeight," +
            "ym:s:purchaseID,ym:s:purchaseDateTime,ym:s:purchaseAffiliation,ym:s:purchaseRevenue," +
            "ym:s:purchaseTax,ym:s:purchaseShipping,ym:s:purchaseCoupon,ym:s:purchaseCurrency," +
            "ym:s:purchaseProductQuantity,ym:s:productsID,ym:s:productsName,ym:s:productsBrand," +
            "ym:s:productsCategory,ym:s:productsCategory1,ym:s:productsCategory2,ym:s:productsCategory3," +
            "ym:s:productsCategory4,ym:s:productsCategory5,ym:s:productsVariant,ym:s:productsPosition," +
            "ym:s:productsPrice,ym:s:productsCurrency,ym:s:productsCoupon,ym:s:productsQuantity," +
            "ym:s:impressionsURL,ym:s:impressionsDateTime,ym:s:impressionsProductID,ym:s:impressionsProductName," +
            "ym:s:impressionsProductBrand,ym:s:impressionsProductCategory,ym:s:impressionsProductCategory1," +
            "ym:s:impressionsProductCategory2,ym:s:impressionsProductCategory3,ym:s:impressionsProductCategory4," +
            "ym:s:impressionsProductCategory5,ym:s:impressionsProductVariant,ym:s:impressionsProductPrice," +
            "ym:s:impressionsProductCurrency,ym:s:impressionsProductCoupon,ym:s:offlineCallTalkDuration," +
            "ym:s:offlineCallHoldDuration,ym:s:offlineCallMissed,ym:s:offlineCallTag," +
            "ym:s:offlineCallFirstTimeCaller,ym:s:offlineCallURL,ym:s:regionArea," +
            "ym:s:isTurboPage,ym:s:isTurboApp,ym:s:adBlock";

    public static final String VISITS_PARSED_PARAMS = "ym:s:parsedParamsKey1,ym:s:parsedParamsKey2," +
            "ym:s:parsedParamsKey3,ym:s:parsedParamsKey4,ym:s:parsedParamsKey5,ym:s:parsedParamsKey6," +
            "ym:s:parsedParamsKey7,ym:s:parsedParamsKey8,ym:s:parsedParamsKey9,ym:s:parsedParamsKey10";

    public static final String VISITS_TIME_AND_PARAMS = "ym:s:dateTime,ym:s:parsedParamsKey1";

    public static final String HITS_FIELDS = "ym:pv:watchID,ym:pv:counterID,ym:pv:dateTime,ym:pv:title,ym:pv:URL," +
            "ym:pv:referer,ym:pv:UTMCampaign,ym:pv:UTMContent,ym:pv:UTMMedium,ym:pv:UTMSource,ym:pv:UTMTerm," +
            "ym:pv:browser,ym:pv:browserMajorVersion,ym:pv:browserMinorVersion,ym:pv:browserCountry," +
            "ym:pv:browserEngine,ym:pv:browserEngineVersion1,ym:pv:browserEngineVersion2," +
            "ym:pv:browserEngineVersion3,ym:pv:browserEngineVersion4,ym:pv:browserLanguage,ym:pv:clientTimeZone," +
            "ym:pv:cookieEnabled,ym:pv:deviceCategory,ym:pv:from,ym:pv:hasGCLID,ym:pv:ipAddress," +
            "ym:pv:javascriptEnabled,ym:pv:mobilePhone,ym:pv:mobilePhoneModel,ym:pv:openstatAd," +
            "ym:pv:openstatCampaign,ym:pv:openstatService,ym:pv:openstatSource,ym:pv:operatingSystem," +
            "ym:pv:operatingSystemRoot,ym:pv:physicalScreenHeight,ym:pv:physicalScreenWidth,ym:pv:regionCity," +
            "ym:pv:regionCountry,ym:pv:screenColors,ym:pv:screenFormat,ym:pv:screenHeight,ym:pv:screenOrientation," +
            "ym:pv:screenWidth,ym:pv:windowClientHeight,ym:pv:windowClientWidth,ym:pv:params," +
            "ym:pv:lastTrafficSource,ym:pv:lastSearchEngine,ym:pv:lastSearchEngineRoot,ym:pv:lastAdvEngine," +
            "ym:pv:artificial,ym:pv:pageCharset,ym:pv:link,ym:pv:download,ym:pv:notBounce,ym:pv:lastSocialNetwork," +
            "ym:pv:httpError,ym:pv:clientID,ym:pv:networkType,ym:pv:lastSocialNetworkProfile,ym:pv:goalsID," +
            "ym:pv:shareService,ym:pv:shareURL,ym:pv:shareTitle,ym:pv:iFrame,ym:pv:date," +
            "ym:pv:regionArea,ym:pv:regionAreaID,ym:pv:isTurboPage,ym:pv:isTurboApp,ym:pv:adBlock";
}
