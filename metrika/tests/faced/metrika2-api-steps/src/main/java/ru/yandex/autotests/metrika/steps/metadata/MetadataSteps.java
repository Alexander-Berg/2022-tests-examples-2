package ru.yandex.autotests.metrika.steps.metadata;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.commons.lang3.tuple.Pair;
import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.SubTable;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.metadata.v1.ConstructorParameters;
import ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.autotests.metrika.utils.Utils;
import ru.yandex.metrika.api.constructor.presets.PresetExternal;
import ru.yandex.metrika.api.constructor.response.DimensionMetaExternal;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;
import ru.yandex.metrika.api.management.client.autogoals.PartnerGoal;
import ru.yandex.metrika.managers.Currency;
import ru.yandex.metrika.segments.site.parametrization.Attribution;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.function.BiFunction;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toMap;
import static org.hamcrest.Matchers.empty;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.CurrencyParameters.currency;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters.parametrization;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.*;
import static ru.yandex.autotests.metrika.utils.Utils.removeNamespace;

/**
 * Created by konkov on 04.08.2014.
 * Шаги для работы с метаданными
 */
public class MetadataSteps extends MetrikaBaseSteps {

    /**
     * Константы путей к ручкам
     */
    private static class Handles {
        private static final String METRICS_RAW_PATH = "/stat/v1/metadata/constructor_documented_metrics_api";
        private static final String METRICS_CONSTRUCTOR_RAW_PATH = "/stat/v1/metadata/constructor_metrics";
        private static final String METRICS_PATH_COMPACT = "/stat/v1/metadata/constructor_documented_metrics_api_compact";
        private static final String DIMENSIONS_RAW_PATH = "/stat/v1/metadata/constructor_documented_attributes_api";
        private static final String DIMENSIONS_PATH_COMPACT = "/stat/v1/metadata/constructor_documented_attributes_api_compact";
        private static final String SEGMENTS_PATH_COMPACT = "/stat/v1/metadata/segments_compact";
        private static final String PRESETS_PATH = "/stat/v1/metadata/presets";
        private static final String CURRENCY_PATH = "/internal/management/v1/currency";
        private static final String GA_METRICS_PATH_COMPACT = "/analytics/v3/metadata/constructor_documented_metrics_api_compact";
        private static final String GA_DIMENSIONS_PATH_COMPACT = "/analytics/v3/metadata/constructor_documented_attributes_api_compact";
        private static final String CLIMETR_CONFIG_RAW_PATH = "/stat/v1/metadata/climetr";
        private static final String CLIMETR_CONFIG_COUNTER_PATH = "/stat/v1/metadata/climetr/";
        private static final String PARTNERS_GOALS_TYPES_PATH = "/management/v1/partners/goals_types";
    }

    /**
     * Константы захардкоженных списков
     */
    private static class Sets {

        public static final List<String> METRICS_ECOMMERCE = ImmutableList.of(
                "ym:s:usersPurchasePercentage",
                "ym:s:ecommercePurchases",
                "ym:s:productBasketsQuantity",
                "ym:s:productBasketsUniq",
                "ym:s:productImpressions",
                "ym:s:productImpressionsUniq",
                "ym:s:productPurchasedQuantity",
                "ym:s:productPurchasedUniq",
                "ym:s:productBaskets<currency>Price",
                "ym:s:productBaskets<currency>ConvertedPrice",
                "ym:s:productBasketsPrice",
                "ym:s:productPurchased<currency>Price",
                "ym:s:productPurchased<currency>ConvertedPrice",
                "ym:s:productPurchasedPrice",
                "ym:s:ecommerce<currency>Revenue",
                "ym:s:ecommerce<currency>ConvertedRevenue",
                "ym:s:ecommerceRevenue",
                "ym:s:ecommerce<currency>RevenuePerPurchase",
                "ym:s:ecommerce<currency>ConvertedRevenuePerPurchase",
                "ym:s:ecommerceRevenuePerPurchase",
                "ym:s:ecommerce<currency>RevenuePerVisit",
                "ym:s:ecommerce<currency>ConvertedRevenuePerVisit",
                "ym:s:ecommerceRevenuePerVisit",
                "ym:s:productBasketsAddQuantity",
                "ym:s:productBasketsRemoveQuantity",
                "ym:s:productBasketsAdd<currency>Price",
                "ym:s:productBasketsAdd<currency>ConvertedPrice",
                "ym:s:productBasketsAddPrice",
                "ym:s:productBasketsRemove<currency>Price",
                "ym:s:productBasketsRemove<currency>ConvertedPrice",
                "ym:s:productBasketsRemovePrice"
        );

        public static final List<String> METRICS_ADVERTISING_ECOMMERCE = ImmutableList.of(
                "ym:ad:ecommercePurchases",
                "ym:ad:ecommerceRevenue",
                "ym:ad:ecommerce<currency>Revenue",
                "ym:ad:ecommerce<currency>ConvertedRevenue",
                "ym:ad:ecommerceRevenuePerPurchase",
                "ym:ad:ecommerce<currency>RevenuePerPurchase",
                "ym:ad:ecommerce<currency>ConvertedRevenuePerPurchase",
                "ym:ad:ecommerceRevenuePerVisit",
                "ym:ad:ecommerce<currency>RevenuePerVisit",
                "ym:ad:ecommerce<currency>ConvertedRevenuePerVisit",
                "ym:ad:productBasketsPrice",
                "ym:ad:productBaskets<currency>Price",
                "ym:ad:productBaskets<currency>ConvertedPrice",
                "ym:ad:productBasketsQuantity",
                "ym:ad:productBasketsAdd<currency>Price",
                "ym:ad:productBasketsAdd<currency>ConvertedPrice",
                "ym:ad:productBasketsAddPrice",
                "ym:ad:productBasketsAddQuantity",
                "ym:ad:productBasketsRemovePrice",
                "ym:ad:productBasketsRemove<currency>Price",
                "ym:ad:productBasketsRemove<currency>ConvertedPrice",
                "ym:ad:productBasketsRemoveQuantity",
                "ym:ad:productBasketsUniq",
                "ym:ad:productImpressions",
                "ym:ad:productImpressionsUniq",
                "ym:ad:productPurchasedPrice",
                "ym:ad:productPurchased<currency>Price",
                "ym:ad:productPurchased<currency>ConvertedPrice",
                "ym:ad:productPurchasedQuantity",
                "ym:ad:productPurchasedUniq"
        );

        public static final List<String> DIMENSIONS_ECOMMERCE = ImmutableList.of(
                "ym:s:productBrand",
                "ym:s:productCategoryLevel1",
                "ym:s:productCategoryLevel2",
                "ym:s:productCategoryLevel3",
                "ym:s:productCategoryLevel4",
                "ym:s:productCategoryLevel5",
                "ym:s:productCurrency",
                "ym:s:productName",
                "ym:s:productPosition",
                "ym:s:productPrice",
                "ym:s:productQuantity",
                "ym:s:productSum",
                "ym:s:productVariant",
                "ym:s:purchaseCount",
                "ym:s:purchaseCoupon",
                "ym:s:purchaseID",
                "ym:s:purchaseRevenue",
                "ym:s:productCoupon",
                "ym:s:productBrandCart",
                "ym:s:productNameCart",
                "ym:s:purchaseCountVisit",
                "ym:s:impressionCountVisit"
        );

        public static final List<String> PRESETS_ECOMMERCE = ImmutableList.of(
                "top_products",
                "top_brands",
                "basket",
                "purchase",
                "coupon",
                "basket_products"
        );

        public static final List<String> DIMENSIONS_ECOMMERCE_ORDERS = ImmutableList.of(
                "ym:s:purchaseID",
                "ym:s:PProduct");

        public static final List<String> METRICS_ECOMMERCE_ORDERS = ImmutableList.of(
                "ym:s:pProductPurchasedQuantity",
                "ym:s:pProductPurchasedRevenue");

        public static final List<String> NON_UNIQUE_METRICS = ImmutableList.of(
                "ym:s:visits",
                "ym:s:sumParams",
                "ym:s:goal<goal_id>reaches",
                "ym:s:goal<goal_id>revenue",
                "ym:s:goal<goal_id>converted<currency>Revenue",
                "ym:ad:ecommercePurchases",
                "ym:ad:clicks",
                "ym:pv:pageviews",
                "ym:el:links",
                "ym:dl:downloads",
                "ym:sp:sumHitsForAllHits"
        );

        /**
         * Специально отобранные метрики. Из каждого namespace с различными типами.
         */
        public static final List<String> FAVORITE_METRICS = ImmutableList.of(
                "ym:s:users",
                "ym:s:affinityIndexInterests",
                "ym:s:ecommerceRevenuePerPurchase",
                "ym:s:avgVisitDurationSeconds",
                "ym:s:visitsPerDay",
                "ym:s:blockedPercentage",
                "ym:s:goal<goal_id>visits",
                "ym:s:goal<goal_id><currency>revenue",
                "ym:s:goal<goal_id>converted<currency>Revenue",
                "ym:s:sumParams",
                "ym:pv:pageviews",
                "ym:pv:blockedPercentage",
                "ym:pv:pageviewsPerDay",
                "ym:sp:sumHitsForAllHits",
                "ym:sp:blockedPercentage",
                "ym:sp:qTime<quantile>TimingsResponse",
                "ym:sp:pageviewsPerDay",
                "ym:sh:users",
                "ym:el:blockedPercentage",
                "ym:el:pageviewsPerDay",
                "ym:el:links",
                "ym:dl:pageviewsPerDay",
                "ym:dl:blockedPercentage",
                "ym:dl:downloads",
                "ym:ad:users",
                "ym:ad:<currency>AdCostPerVisit",
                "ym:ad:<currency>ConvertedAdCostPerVisit",
                "ym:ad:affinityIndexInterests",
                "ym:ad:visitsPerDay",
                "ym:ad:manPercentage",
                "ym:ad:avgVisitDurationSeconds",
                "ym:ad:goal<goal_id><currency>CPA",
                "ym:ad:goal<goal_id>converted<currency>CPA",
                "ym:ad:goal<goal_id>visits",
                "ym:ad:sumParams",
                "ym:up:users",
                "ym:up:params"
        );

        /**
         * Специально отобранные измерения. Из каждого namespace с различными типами.
         */
        public static final List<String> FAVORITE_DIMENSIONS = ImmutableList.of(
                "ym:s:<attribution>SearchEngine",
                "ym:s:<attribution>DirectBanner",
                "ym:s:datePeriod<group>",
                "ym:s:gender",
                "ym:s:paramsLevel1",
                "ym:pv:datePeriod<group>",
                "ym:pv:gender",
                "ym:sp:datePeriod<group>",
                "ym:sp:gender",
                "ym:sh:datePeriod<group>",
                "ym:sh:gender",
                "ym:el:datePeriod<group>",
                "ym:el:gender",
                "ym:dl:datePeriod<group>",
                "ym:dl:gender",
                "ym:ad:gender",
                "ym:ad:<attribution>DirectBanner",
                "ym:u:interest",
                "ym:up:paramsLevel1"
        );
        /**
         * Отобранные вручную значения измерений для тестов сегментации inpage
         */
        public static final List<String> INPAGE_FAVORITE_DIMENSIONS = ImmutableList.of(
                "ym:s:trafficSource",
                "ym:s:searchEngineRoot",
                "ym:s:searchPhrase",
                "ym:s:hasAdBlocker",
                "ym:s:hour",
                "ym:s:paramsLevel1",
                "ym:s:referer",
                "ym:s:startURL",
                "ym:s:gender"
        );
        /**
         * Отобранные вручную значения измерений для тестов глобальных отчетов
         */
        public static final List<String> GLOBAL_FAVORITE_DIMENSIONS = ImmutableList.of(
                "ym:dl:ageInterval",
                "ym:el:browserCountry",
                "ym:pv:URLPathLevel1Has",
                "ym:s:physicalScreenHeight",
                "ym:s:interest",
                "ym:sp:clientTimeZone",
                "ym:sh:browserAndVersion",
                "ym:sh:browserEngine",
                "ym:pv:date"
        );

        public static final List<String> OFFLINE_CALLS_METRICS = ImmutableList.of(
                "ym:s:offlineCalls",
                "ym:s:offlineCallsAnswered",
                "ym:s:offlineCallsAnsweredPercentage",
                "ym:s:offlineCallsMissed",
                "ym:s:offlineCallsMissedPercentage",
                "ym:s:offlineCallsFirstTimeCaller",
                "ym:s:offlineCallsFirstTimeCallerPercentage",
                "ym:s:offlineCallsUniq",
                "ym:s:offlineCallTalkDurationAvg",
                "ym:s:offlineCallHoldDurationAvg",
                "ym:s:offlineCallHoldDurationTillAnswerAvg",
                "ym:s:offlineCallHoldDurationTillMissAvg",
                "ym:s:offlineCallDurationAvg",
                "ym:s:offlineCallRevenueAvg",
                "ym:s:offlineCall<currency>RevenueAvg",
                "ym:s:offlineCall<currency>ConvertedRevenueAvg",
                "ym:s:offlineCallRevenue",
                "ym:s:offlineCall<currency>Revenue",
                "ym:s:offlineCall<currency>ConvertedRevenue"
        );

        public static final List<String> OFFLINE_CALLS_DIMENSIONS = ImmutableList.of(
                "ym:s:offlineCallEventTime",
                "ym:s:offlineCallRevenue",
                "ym:s:offlineCall<currency>Revenue",
                "ym:s:offlineCall<currency>ConvertedRevenue",
                "ym:s:offlineCallPhoneNumber",
                "ym:s:offlineCallTalkDuration",
                "ym:s:offlineCallHoldDuration",
                "ym:s:offlineCallDuration",
                "ym:s:offlineCallHoldDurationTillAnswer",
                "ym:s:offlineCallHoldDurationTillMiss",
                "ym:s:offlineCallMissed",
                "ym:s:offlineCallMissedName",
                "ym:s:offlineCallTag",
                "ym:s:offlineCallFirstTimeCaller",
                "ym:s:offlineCallFirstTimeCallerName",
                "ym:s:offlineCallURL",
                "ym:s:offlineCallTrackerURL"
        );

        public static final List<String> OFFLINE_CALLS_PRESETS = ImmutableList.of(
                "offline_calls_sources",
                "offline_calls_quality"
        );

        public static final List<String> YAN_METRICS = ImmutableList.of(
                "ym:s:yanRequests",
                "ym:s:yanRenders",
                "ym:s:yanShows",
                "ym:s:yanPartnerPrice",
                "ym:s:yanCPMV",
                "ym:s:yanECPM",
                "ym:s:yanRPM",
                "ym:s:yanVisibility",
                "ym:s:yanARPU",
                "ym:s:yanRendersPerUser",
                "ym:s:yanRendersPerVisit",
                "ym:s:yanRendersPerHit",
                "ym:s:yanRevenuePerVisit",
                "ym:s:yanRevenuePerHit"
        );

        public static final List<String> YAN_DIMENSIONS = ImmutableList.of(
                "ym:s:yanPageID",
                "ym:s:yanBlockID",
                "ym:s:yanBlockSize",
                "ym:s:yanIsAdBlock",
                "ym:s:yanUrl",
                "ym:s:yanUrlHash",
                "ym:s:yanUrlPathLevel1",
                "ym:s:yanUrlPathLevel2",
                "ym:s:yanUrlPathLevel3",
                "ym:s:yanUrlPathLevel4",
                "ym:s:yanUrlPathLevel1Hash",
                "ym:s:yanUrlPathLevel2Hash",
                "ym:s:yanUrlPathLevel3Hash",
                "ym:s:yanUrlPathLevel4Hash"
        );

        public static final List<String> YAN_PRESETS = ImmutableList.of(
                "yan",
                "yan_sources",
                "yan_geo",
                "yan_device",
                "yan_browsers",
                "yan_adb"
        );

        public static final List<String> NDA_METRICS = ImmutableList.of(
                "ym:s:javaEnabledPercentage",
                "ym:el:flashEnabledPercentage",
                "ym:pv:silverlightEnabledPercentage",
                "ym:sp:flashEnabledPercentage",
                "ym:s:YCLIDPercentage",
                "ym:s:YACLIDPercentage",
                "ym:s:YDCLIDPercentage",
                "ym:s:YMCLIDPercentage",
                "ym:s:depthGT2percent",
                "ym:s:depthGT3percent",
                "ym:s:depthGT5percent",
                "ym:s:durationGT30percent",
                "ym:s:durationGT120percent",
                "ym:s:durationGT300percent",
                "ym:s:durationGT900percent",
                "ym:s:uniqIp",
                "ym:s:uniqIp4",
                "ym:s:uniqIp6",
                "ym:pv:UserID",
                "ym:s:CryptaID"
        );

        public static final List<String> NDA_DIMENSIONS = ImmutableList.of(
                "ym:s:firstDirectBannerText",
                "ym:s:ASN",
                "ym:s:inYandexRegion",
                "ym:s:ip",
                "ym:s:ip4",
                "ym:s:ip6",
                "ym:dl:UIDCreateDate",
                "ym:s:YACLID",
                "ym:sh:YMCLID",
                "ym:pv:YDCLID",
                "ym:s:codeVersion",
                "ym:s:counterClass",
                "ym:s:counterIDSerial",
                "ym:s:flashEnabled",
                "ym:s:hasYACLID",
                "ym:s:javaEnabled",
                "ym:dl:moscowDate",
                "ym:s:moscowDayOfMonth",
                "ym:dl:silverlight",
                "ym:pv:userIDString",
                "ym:el:CLID",
                "ym:pv:turboPageID",
                "ym:s:isLoggedIn",
                "ym:s:isRobotInternal",
                "ym:s:isYandex",
                "ym:s:networkType",
                "ym:s:passportUserID",
                "ym:s:userIDBucket",
                "ym:s:visitIDBucket",
                "ym:s:yandexLogin"
        );

        public static final List<String> VACUUM_PRESETS = ImmutableList.of(
                "vacuum"
        );

        public static final List<String> CDP_PRESETS = ImmutableList.of(
                "cdp_orders",
                "orders_sources",
                "sources_expenses_and_roi"
        );

        public static final List<String> RECOMMENDATION_WIDGET_PRESETS = ImmutableList.of(
                "recommendation_widget_articles",
                "recommendation_widget_conversion",
                "recommendation_widget_page"
        );

        public static final List<String> INTEREST2_METRICS = ImmutableList.of(
                "ym:s:affinityIndexInterests2"
        );
        public static final List<String> INTEREST2_NAME_DIMENSIONS = ImmutableList.of(
                "ym:s:interest2Name1",
                "ym:s:interest2Name2",
                "ym:s:interest2Name3"
        );
        public static final List<String> INTEREST2_VALUE_DIMENSIONS = ImmutableList.of(
                "ym:s:interest2d1",
                "ym:s:interest2d2",
                "ym:s:interest2d3"
        );
        public static final List<String> INTEREST2_DIMENSIONS = ImmutableList.<String>builder()
                .addAll(INTEREST2_NAME_DIMENSIONS)
                .addAll(INTEREST2_VALUE_DIMENSIONS)
                .build();

        public static final List<String> PUBLISHERS_METRICS = ImmutableList.of(
                "ym:s:sumPublisherArticleInvolvedTimeSeconds",
                "ym:s:avgPublisherArticleInvolvedTimeSeconds",
                "ym:s:sumEventInvolvedTimeSeconds",
                "ym:s:avgEventInvolvedTimeSeconds",
                "ym:s:publisherviews",
                "ym:s:publisherviewsPerWeek",
                "ym:s:publisherviewsPerDay",
                "ym:s:publisherviewsPerHour",
                "ym:s:publisherviewsPerDekaminute",
                "ym:s:publisherviewsPerMinute",
                "ym:s:publisherusers",
                "ym:s:publisherArticleViewsRecircled",
                "ym:s:publisherArticleUsersRecircled",
                "ym:s:publisherArticleRecirculation",
                "ym:s:publisherViewsFullScroll",
                "ym:s:publisherArticleViewsFullScrollShare",
                "ym:s:publisherViewsFullRead",
                "ym:s:publisherArticleFullReadShare",
                "ym:s:publisherMobileOrTabletViews",
                "ym:s:publisherMobileOrTabletViewsShare"
        );

        public static final List<String> PUBLISHERS_DIMENSIONS = ImmutableList.of(
                "ym:s:publisherArticleID",
                "ym:s:publisherArticleTitle",
                "ym:s:publisherArticleRubric",
                "ym:s:publisherArticleRubric2",
                "ym:s:publisherArticleTopics",
                "ym:s:publisherArticleTopic",
                "ym:s:publisherArticleAuthors",
                "ym:s:publisherArticleAuthor",
                "ym:s:publisherArticlePublishedDate",
                "ym:s:publisherArticleURL",
                "ym:s:publisherArticle",
                "ym:s:publisherEventTime",
                "ym:s:publisherArticleScrollDown",
                "ym:s:publisherArticleHasFullScroll",
                "ym:s:publisherArticleReadPart",
                "ym:s:publisherArticleHasFullRead",
                "ym:s:publisherArticleFromTitle",
                "ym:s:publisherArticleHasRecircled",
                "ym:s:publisherTrafficSource",
                "ym:s:publisherTrafficSource2",
                "ym:s:publisherPageFormat",
                "ym:s:publisherLongArticle"
        );

        public static final List<String> VACUUM_METRICS = ImmutableList.of(
                "ym:s:vacuumevents",
                "ym:s:vacuumusers",
                "ym:s:vacuumeventsPerUser"
        );

        public static final List<String> VACUUM_DIMENSIONS = ImmutableList.of(
                "ym:s:vacuumSurface",
                "ym:s:vacuumEvent",
                "ym:s:vacuumOrganization"
        );

        public static final List<String> RECOMMENDATION_WIDGET_METRICS = ImmutableList.of(
                "ym:s:rwShows",
                "ym:s:rwArticleShows",
                "ym:s:rwClicksSum",
                "ym:s:rwArticleClicks",
                "ym:s:rwVisibility",
                "ym:s:rwArticleVisibility",
                "ym:s:rwCTR",
                "ym:s:rwArticleCTR"
        );

        public static final List<String> RECOMMENDATION_WIDGET_DIMENSIONS = ImmutableList.of(
                "ym:s:RWArticleURL",
                "ym:s:RWArticleURLHash",
                "ym:s:RWArticleURLHashName",
                "ym:s:RWArticleURLDomain",
                "ym:s:RWArticleURLPathFull",
                "ym:s:RWArticleURLPath",
                "ym:s:RWArticleURLProto",
                "ym:s:RWArticleURLPathLevel1",
                "ym:s:RWArticleURLPathLevel2",
                "ym:s:RWArticleURLPathLevel3",
                "ym:s:RWArticleURLPathLevel4",
                "ym:s:RWArticleURLPathLevel5",
                "ym:s:RWArticleURLPathLevel1Hash",
                "ym:s:RWArticleURLPathLevel2Hash",
                "ym:s:RWArticleURLPathLevel3Hash",
                "ym:s:RWArticleURLPathLevel4Hash",
                "ym:s:RWArticleURLPathLevel5Hash",
                "ym:s:RWURL",
                "ym:s:RWURLHash",
                "ym:s:RWURLHashName",
                "ym:s:RWURLDomain",
                "ym:s:RWURLPathFull",
                "ym:s:RWURLPath",
                "ym:s:RWURLProto",
                "ym:s:RWURLPathLevel1",
                "ym:s:RWURLPathLevel2",
                "ym:s:RWURLPathLevel3",
                "ym:s:RWURLPathLevel4",
                "ym:s:RWURLPathLevel5",
                "ym:s:RWURLPathLevel1Hash",
                "ym:s:RWURLPathLevel2Hash",
                "ym:s:RWURLPathLevel3Hash",
                "ym:s:RWURLPathLevel4Hash",
                "ym:s:RWURLPathLevel5Hash",
                "ym:s:RWConversion"
        );

        public static final List<String> CURRENCY_CONVERTED_METRICS = ImmutableList.of(
                "ym:s:goal<goal_id>converted<currency>Revenue",
                "ym:s:conversionRateGroup<goal_id>converted<currency>Revenue",
                "ym:ad:conversionRateGroup<goal_id>converted<currency>Revenue",
                "ym:ad:goal<goal_id>converted<currency>Revenue"
        );

        public static final List<String> CURRENCIES = ImmutableList.of(
                "RUB",
                "USD",
                "EUR",
                "TRY",
                "BYN"
        );

        /**
         * Специально отобранные измерения. Hits, visits, advertising.
         */
        public static final List<String> USERCENTRIC_DIMENSIONS = ImmutableList.of(
                "ym:pv:gender",
                "ym:s:gender",
                "ym:ad:gender"
        );

        /**
         * Специально отобранные метрики. Hits, visits, advertising.
         */
        public static final List<String> USERCENTRIC_METRICS = ImmutableList.of(
                "ym:pv:pageviews",
                "ym:s:visits",
                "ym:ad:clicks"
        );

        /**
         * Специально отобранные метрики для счетчика c CDP данными. Hits, visits.
         */
        public static final List<String> CDP_USERCENTRIC_METRICS = ImmutableList.of(
                "ym:pv:pageviews",
                "ym:s:visits"
        );
    }

    /**
     * предикаты для употребления со степами получения списков метрик, измерений, пресетов
     */
    public static class Predicates {

        /**
         * @return предикат - "любой", над любым типом
         */
        public static <T> Predicate<T> any() {
            return m -> true;
        }

        /**
         * @param matcher Hamcrest матчер, которому делегируется логика предиката
         * @return предикат над метаданными метрики, делегирующий вычисление в матчер над именем измерения
         */
        public static Predicate<MetricMetaExternal> metric(Matcher<String> matcher) {
            return m -> matcher.matches(m.getDim());
        }

        /**
         * @param predicate предикат над именем метрики
         * @return предикат над метаданными метрики, делегирующий вычисление предикату над именем метрики
         */
        public static Predicate<MetricMetaExternal> metric(Predicate<String> predicate) {
            return m -> predicate.test(m.getDim());
        }

        /**
         * @param matcher Hamcrest матчер, которому делегируется логика предиката
         * @return предикат над метаданными измерения, делегирующий вычисление в матчер над именем измерения
         */
        public static Predicate<DimensionMetaExternal> dimension(Matcher<String> matcher) {
            return m -> matcher.matches(m.getDim());
        }

        /**
         * @param predicate предикат над именем измерения
         * @return предикат над метаданными измерения, делегирующий вычисление предикату над именем измерения
         */
        public static Predicate<DimensionMetaExternal> dimension(Predicate<String> predicate) {
            return m -> predicate.test(m.getDim());
        }

        /**
         * @param matcher Hamcrest матчер, которому делегируется логика предиката
         * @return предикат над строкой, делегирующий вычисление матчеру
         */
        public static Predicate<String> matches(Matcher<String> matcher) {
            return matcher::matches;
        }

        /**
         * @param table таблица, неймспейс
         * @return предикат принадлежности имени метрики/измерения указанной таблице
         */
        public static Predicate<String> table(TableEnum table) {
            return s -> s.startsWith(table.getNamespace());
        }

        /**
         * @return предикат принадлежности имени метрики/измерения известной таблице
         */
        public static Predicate<String> knownTable() {
            return s -> TableEnum.stream().anyMatch(t -> s.startsWith(t.getNamespace()));
        }

        /**
         * @return предикат того, что метрика/измерение не содержит параметров
         */
        public static Predicate<String> nonParameterized() {
            return m -> ParametrizationTypeEnum.stream()
                    .noneMatch(p -> m.contains(p.getPlaceholder()));
        }

        /**
         * @param parametrization параметр метрики/измерения (параметризация)
         * @return предикат того, что метрика/измерение содержит указанный параметр
         */
        public static Predicate<String> parameterized(ParametrizationTypeEnum parametrization) {
            return m -> m.contains(parametrization.getPlaceholder());
        }

        /**
         * @return предикат того, что метрика поддерживает режим доверия к данным
         */
        public static Predicate<MetricMetaExternal> supportConfidence() {
            return m -> m.getSupportConfidence() != null && m.getSupportConfidence();
        }

        /**
         * @return предикат принадлежности метрики/измерения к ecommerce
         */
        public static Predicate<String> ecommerce() {
            return m -> Sets.METRICS_ECOMMERCE.contains(m)
                    || Sets.METRICS_ADVERTISING_ECOMMERCE.contains(m)
                    || Sets.DIMENSIONS_ECOMMERCE.contains(m);
        }

        /**
         * @return предикат принадлежности метрики/измерения к РСЯ
         */
        public static Predicate<String> yan() {
            return m -> Sets.YAN_METRICS.contains(m)
                    || Sets.YAN_DIMENSIONS.contains(m);
        }

        public static Predicate<String> crossDeviceAttribution() {
            return m -> m.equals("ym:s:crossDeviceUsers");
        }

        /**
         * @return предикат принадлежности метрики/измерения к NDA атрибутам
         */
        public static Predicate<String> nda() {
            return m -> Sets.NDA_METRICS.contains(m)
                    || Sets.NDA_DIMENSIONS.contains(m);
        }

        public static Predicate<String> interest2() {
            return m -> Sets.INTEREST2_DIMENSIONS.contains(m)
                    || Sets.INTEREST2_METRICS.contains(m);
        }

        public static Predicate<String> cdp() {
            return m -> m.contains("cdpOrders");
        }

        public static Predicate<String> goalsCurrency() {
            return Sets.CURRENCY_CONVERTED_METRICS::contains;
        }

        public static Predicate<String> interest2Name() {
            return Sets.INTEREST2_NAME_DIMENSIONS::contains;
        }

        /**
         * @return предикат принадлежности метрики/измерения к специально отобранным
         */
        public static Predicate<String> favorite() {
            return m -> Sets.FAVORITE_METRICS.contains(m)
                    || Sets.FAVORITE_DIMENSIONS.contains(m);
        }

        public static Predicate<MetricMetaExternal> favoriteMetrics() {
            return m -> Sets.FAVORITE_METRICS.contains(m.getDim());
        }

        /**
         * @return предикат принадлежности метрики/измерения не с уникальными значениями
         */
        public static Predicate<String> non_unigue() {
            return m -> Sets.NON_UNIQUE_METRICS.contains(m)
                    || Sets.FAVORITE_DIMENSIONS.contains(m);
        }

        /**
         * @return предикат принадлежности метрики/измерения к специально отобранным для inpage
         */
        public static Predicate<String> favoriteInpage() {
            return Sets.INPAGE_FAVORITE_DIMENSIONS::contains;
        }

        /**
         * @return предикат принадлежности метрики/измерения к специально отобранным для глобальных отчетов
         */
        public static Predicate<String> favoriteGlobal() {
            return Sets.GLOBAL_FAVORITE_DIMENSIONS::contains;
        }

        /**
         * @return предикат того, что измерение содержит url
         */
        public static Predicate<DimensionMetaExternal> url() {
            return m -> (StringUtils.equals(m.getType(), "url")
                    || StringUtils.equals(m.getType(), "url-part"))
                    && !m.getDim().endsWith("Hash");
        }

        /**
         * @return предикат принадлежности метрики/измерения к офлайн звонкам
         */
        public static Predicate<String> offlineCalls() {
            return m -> Sets.OFFLINE_CALLS_METRICS.contains(m)
                    || Sets.OFFLINE_CALLS_DIMENSIONS.contains(m);
        }

        public static Predicate<String> publishers() {
            return m -> Sets.PUBLISHERS_DIMENSIONS.contains(m)
                    || Sets.PUBLISHERS_METRICS.contains(m);
        }

        public static Predicate<String> vacuum() {
            return m -> Sets.VACUUM_DIMENSIONS.contains(m)
                    || Sets.VACUUM_METRICS.contains(m);
        }

        public static Predicate<String> recommendationWidget() {
            return m -> Sets.RECOMMENDATION_WIDGET_DIMENSIONS.contains(m)
                    || Sets.RECOMMENDATION_WIDGET_METRICS.contains(m);
        }

        public static Predicate<String> syntaxUserCentric() {
            return m -> Sets.USERCENTRIC_DIMENSIONS.contains(m)
                    || Sets.USERCENTRIC_METRICS.contains(m);
        }

        public static Predicate<String> syntaxCdpUserCentric() {
            return m -> Sets.USERCENTRIC_DIMENSIONS.contains(m)
                    || Sets.CDP_USERCENTRIC_METRICS.contains(m);
        }

        public static class Dimension {
            /**
             * @param subTable подтаблица (множество)
             * @return предикат принадлежности измерения множеству
             */
            public static Predicate<DimensionMetaExternal> subTable(SubTable subTable) {
                return m -> StringUtils.equals(m.getSubTable(), subTable.toString());
            }
        }

        public static class Metric {
            /**
             * @param subTable подтаблица (множество)
             * @return предикат принадлежности измерения множеству
             */
            public static Predicate<MetricMetaExternal> subTable(SubTable subTable) {
                return m -> StringUtils.equals(m.getSubTable(), subTable.toString());
            }
        }

        public static class Preset {
            /**
             * @param table таблица, неймспейс
             * @return предикат принадлежности пресета к указанной таблице
             */
            public static Predicate<PresetExternal> table(TableEnum table) {
                return p -> StringUtils.equals(p.getTable(), table.getValue());
            }

            /**
             * @return предикат принадлежности пресета к ecommerce
             */
            public static Predicate<PresetExternal> ecommerce() {
                return p -> Sets.PRESETS_ECOMMERCE.contains(p.getName());
            }

            public static Predicate<PresetExternal> experimentAB() {
                return p -> "experiment_ab".equals(p.getName());
            }

            /**
             * @return предикат принадлежности пресета к офлайн звонкам
             */
            public static Predicate<PresetExternal> offlineCalls() {
                return p -> Sets.OFFLINE_CALLS_PRESETS.contains(p.getName());
            }

            /**
             * @return предикат принадлежности пресета к офлайн звонкам
             */
            public static Predicate<PresetExternal> yan() {
                return p -> Sets.YAN_PRESETS.contains(p.getName());
            }

            /**
             * @return предикат принадлежности пресета к cdp
             */
            public static Predicate<PresetExternal> cdp() {
                return p -> Sets.CDP_PRESETS.contains(p.getName());
            }

            public static Predicate<PresetExternal> vacuum() {
                return p -> Sets.VACUUM_PRESETS.contains(p.getName());
            }

            public static Predicate<PresetExternal> recommendationWidget() {
                return p -> Sets.RECOMMENDATION_WIDGET_PRESETS.contains(p.getName());
            }
        }

    }

    public static class Modifiers {
        public static <T> BiFunction<T, FreeFormParameters,
                Stream<Pair<T, FreeFormParameters>>> setParameters(Function<T, IFormParameters> createFunction) {
            return (m, p) ->
                    Stream.of(ImmutablePair.of(m, FreeFormParameters.makeParameters()
                            .append(p).append(createFunction.apply(m))));
        }

        public static <T> BiFunction<T, FreeFormParameters,
                Stream<Pair<T, FreeFormParameters>>> setParameters(IFormParameters parameters) {
            return setParameters(t -> parameters);
        }

        public static <T> BiFunction<T, Object[], Stream<Pair<T, Object[]>>> addParameters(Object[][] params) {
            return (m, p) ->
                    Stream.of(params).map(c -> ImmutablePair.of(m, c));
        }

        public static <T> BiFunction<T, FreeFormParameters,
                Stream<Pair<T, FreeFormParameters>>> addAttributions() {
            return (m, p) ->
                    Stream.of(Attribution.values())
                            .map(a -> ImmutablePair.of(m,
                                    FreeFormParameters.makeParameters()
                                            .append(p)
                                            .append(parametrization().withAttribution(a))));
        }

        public static <T> BiFunction<T, FreeFormParameters,
                Stream<Pair<T, FreeFormParameters>>> addGroups() {
            return (m, p) ->
                    Stream.of(GroupEnum.values())
                            .map(g -> ImmutablePair.of(m,
                                    FreeFormParameters.makeParameters()
                                            .append(p)
                                            .append(parametrization().withGroup(g))));
        }

        public static <T> BiFunction<T, FreeFormParameters,
                Stream<Pair<T, FreeFormParameters>>> addCurrencies() {
            return (m, p) ->
                    Sets.CURRENCIES.stream()
                            .map(c -> ImmutablePair.of(m,
                                    FreeFormParameters.makeParameters()
                                            .append(p)
                                            .append(currency(c))));
        }

    }

    @Step("Получить массив поддерживаемых валют")
    public String[] getAvailableCurrencies() {
        return getResponse(Handles.CURRENCY_PATH)
                .readResponse(InternalManagementV1CurrencyGETSchema.class)
                .getCurrency()
                .stream()
                .map(Currency::getCode)
                .toArray(String[]::new);
    }

    @Step("Получить метрики, удовлетворяющие предикату")
    public Collection<String> getMetrics(Predicate<String> predicate) {
        return getMetricsRaw(metric(predicate));
    }

    @Step("Получить метрики, удовлетворяющие предикату")
    public Collection<String> getMetricsRaw(Predicate<MetricMetaExternal> predicate) {
        return getMetricsMeta(predicate)
                .stream()
                .map(MetricMetaExternal::getDim)
                .collect(toList());
    }

    @Step("Получить метаданные метрик, удовлетворяющие предикату")
    public Collection<MetricMetaExternal> getMetricsMeta(Predicate<MetricMetaExternal> predicate) {
        return getResponse(Handles.METRICS_RAW_PATH)
                .readResponse(StatV1MetadataConstructorDocumentedMetricsApiGETSchema.class)
                .getMetrics()
                .stream()
                .filter(metric(knownTable()).and(predicate))
                .collect(toList());
    }

    @Step("Получить группировки, удовлетворяющие предикату")
    public Collection<String> getDimensions(Predicate<String> predicate) {
        return getDimensionsRaw(dimension(predicate));
    }

    @Step("Получить группировки, удовлетворяющие предикату")
    public Collection<String> getDimensionsRaw(Predicate<DimensionMetaExternal> predicate) {
        return getDimensionsMeta(predicate)
                .stream()
                .map(DimensionMetaExternal::getDim)
                .collect(toList());
    }

    @Step("Получить метаданные группировок, удовлетворяющих предикату")
    public Collection<DimensionMetaExternal> getDimensionsMeta(Predicate<DimensionMetaExternal> predicate) {
        return getResponse(Handles.DIMENSIONS_RAW_PATH)
                .readResponse(StatV1MetadataConstructorDocumentedAttributesApiGETSchema.class)
                .getAttributes()
                .stream()
                .filter(dimension(knownTable()).and(predicate))
                .collect(toList());
    }

    @Step("Получить конфиг для приложения")
    public StatV1MetadataClimetrGETSchema getClimetrConfig() {
        return getResponse(Handles.CLIMETR_CONFIG_RAW_PATH)
                .readResponse(StatV1MetadataClimetrGETSchema.class);
    }

    @Step("Получить конфиг для счетчика")
    public StatV1MetadataClimetrCounterIdGETSchema getClimetrConfig(long counterId) {
        return getResponse(Handles.CLIMETR_CONFIG_COUNTER_PATH + counterId)
                .readResponse(StatV1MetadataClimetrCounterIdGETSchema.class);
    }

    @Step("Получить пресеты удовлетворяющие предикату")
    public Collection<PresetExternal> getPresetsMeta(Predicate<PresetExternal> predicate) {
        return getResponse(Handles.PRESETS_PATH)
                .readResponse(StatV1MetadataPresetsGETSchema.class)
                .getPresets()
                .stream()
                .filter(predicate)
                .collect(toList());
    }

    @Step("Получить пресеты удовлетворяющие предикату")
    public Collection<String> getPresetsRaw(Predicate<PresetExternal> predicate) {
        return getResponse(Handles.PRESETS_PATH)
                .readResponse(StatV1MetadataPresetsGETSchema.class)
                .getPresets()
                .stream()
                .filter(predicate)
                .map(PresetExternal::getName)
                .collect(toList());
    }

    @Step("Получить список всех измерений для фильтрации удовлетворяющие предикату")
    public Collection<String> getAllFilterableDimensions(Predicate<String> predicate) {
        return getResponse(Handles.SEGMENTS_PATH_COMPACT)
                .readResponse(StatV1MetadataSegmentsCompactGETSchema.class)
                .getList()
                .stream()
                .filter(predicate)
                .collect(toList());
    }

    @Step("Получить список всех типов партнёрских целей")
    public Collection<String> getAllPartnersGoalsTypes() {
        return getResponse(Handles.PARTNERS_GOALS_TYPES_PATH)
                .readResponse(ManagementV1PartnersGoalsTypesGETSchema.class)
                .getResponse()
                .stream()
                .map(PartnerGoal::toString)
                .collect(Collectors.toList());
    }


    /**
     * Получить метрики из специальной ручки в которой все существующие метрики.
     * Метод предназначен для того, что бы построить отображение метрик по кликам Директа на count-метрики.
     * Сигнатура содержит явное указание таблицы, а не предикат для того, что бы размер ответа был меньше и попытка
     * его залогировать не вызывала OOM.
     * <p>
     * Для использования в тестах не предназначен.
     *
     * @param table - таблица (неймспейс) из которой нужно получить метрики
     * @return коллекция наименований метрик указанного неймспейса.
     */
    private Collection<String> getConstructorMetricsInternal(TableEnum table) {
        return getResponse(Handles.METRICS_CONSTRUCTOR_RAW_PATH, new ConstructorParameters().withTable(table))
                .readResponse(StatV1MetadataConstructorDocumentedMetricsApiGETSchema.class)
                .getMetrics()
                .stream()
                .map(MetricMetaExternal::getDim)
                .collect(toList());
    }

    @Step("Получить отображение метрик по кликам Директа на count-метрики")
    public Map<String, String> getThresholdAdvertisingMetrics() {
        Collection<String> adMetrics = getMetricsRaw(metric(table(TableEnum.ADVERTISING)).and(supportConfidence()));

        Collection<String> clicks = getConstructorMetricsInternal(TableEnum.CLICKS)
                .stream().map(Utils::removeNamespace).collect(toList());
        Collection<String> clickStorage = getConstructorMetricsInternal(TableEnum.CLICK_STORAGE)
                .stream().map(Utils::removeNamespace).collect(toList());


        List<String> neither = adMetrics.stream().filter(m -> {
            m = removeNamespace(m);
            return !clicks.contains(m) && !clickStorage.contains(m);
        }).collect(toList());

        assumeThat("метрики по кликам Директа присутствуют хотя бы в одной из таблиц",
                neither, empty());

        List<String> both = adMetrics.stream().filter(m -> {
            m = removeNamespace(m);
            return clicks.contains(m) && clickStorage.contains(m);
        }).collect(toList());

        assumeThat("метрики по кликам Директа присутствуют только в одной из таблиц",
                both, empty());

        return adMetrics.stream().filter(m -> !neither.contains(m) && !both.contains(m))
                .map(m -> {
                    if (clicks.contains(removeNamespace(m))) {
                        return ImmutablePair.of(m, "ym:ad:visits");
                    } else {
                        return ImmutablePair.of(m, "ym:ad:clicks");
                    }
                }).collect(toMap(Pair::getKey, Pair::getValue));
    }

    @Step("Получить список всех метрик ecommerce отчета 'Содержимое заказов'")
    public Collection<String> getMetricsEcommerceOrders() {
        return Sets.METRICS_ECOMMERCE_ORDERS;
    }

    @Step("Получить список измерений ecommerce отчета 'Содержимое заказов'")
    public Collection<String> getDimensionsEcommerceOrders() {
        return Sets.DIMENSIONS_ECOMMERCE_ORDERS;
    }

    @Step("Получить все метрики API совместимого с Google Analytics")
    public Collection<String> getAnalyticsMetrics(Predicate<String> predicate) {
        return getResponse(Handles.GA_METRICS_PATH_COMPACT)
                .readResponse(StatV1MetadataSegmentsCompactGETSchema.class)
                .getList()
                .stream()
                .filter(predicate)
                .collect(toList());
    }

    @Step("Получить все измерения API совместимого с Google Analytics")
    public Collection<String> getAnalyticsDimensions(Predicate<String> predicate) {
        return getResponse(Handles.GA_DIMENSIONS_PATH_COMPACT)
                .readResponse(StatV1MetadataSegmentsCompactGETSchema.class)
                .getList()
                .stream()
                .filter(predicate)
                .collect(toList());
    }
}
