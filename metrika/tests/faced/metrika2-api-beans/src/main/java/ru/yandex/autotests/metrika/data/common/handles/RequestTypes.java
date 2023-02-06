package ru.yandex.autotests.metrika.data.common.handles;

import ru.yandex.autotests.metrika.beans.schemes.*;

import static ru.yandex.autotests.metrika.data.common.handles.RequestType.report;

/**
 * Created by konkov on 13.07.2016.
 */
public final class RequestTypes {
    private RequestTypes() {}

    /* Публичные отчеты */

    public static final RequestType<StatV1DataGETSchema> TABLE = report(
            "TABLE",
            StatV1DataGETSchema.class,
            "/stat/v1/data");

    public static final RequestType<StatV1DataDrilldownGETSchema> DRILLDOWN = report(
            "DRILLDOWN",
            StatV1DataDrilldownGETSchema.class,
            "/stat/v1/data/drilldown");

    public static final RequestType<StatV1DataBytimeGETSchema> BY_TIME = report(
            "BY_TIME",
            StatV1DataBytimeGETSchema.class,
            "/stat/v1/data/bytime");

    public static final RequestType<StatV1DataComparisonGETSchema> COMPARISON = report(
            "COMPARISON",
            StatV1DataComparisonGETSchema.class,
            "/stat/v1/data/comparison");

    public static final RequestType<StatV1DataComparisonDrilldownGETSchema> COMPARISON_DRILLDOWN = report(
            "COMPARISON_DRILLDOWN",
            StatV1DataComparisonDrilldownGETSchema.class,
            "/stat/v1/data/comparison/drilldown");

    /* Глобальный отчет */

    public static final RequestType<StatV1DataGETSchema> GLOBAL_TABLE = report(
            "TABLE",
            StatV1DataGETSchema.class,
            "/stat/v1/global");

    public static final RequestType<StatV1DataDrilldownGETSchema> GLOBAL_DRILLDOWN = report(
            "DRILLDOWN",
            StatV1DataDrilldownGETSchema.class,
            "/stat/v1/global/drilldown");

    public static final RequestType<StatV1DataBytimeGETSchema> GLOBAL_BY_TIME = report(
            "BY_TIME",
            StatV1DataBytimeGETSchema.class,
            "/stat/v1/global/bytime");

    public static final RequestType<StatV1DataComparisonGETSchema> GLOBAL_COMPARISON = report(
            "COMPARISON",
            StatV1DataComparisonGETSchema.class,
            "/stat/v1/global/comparison");

    public static final RequestType<StatV1DataComparisonDrilldownGETSchema> GLOBAL_COMPARISON_DRILLDOWN = report(
            "COMPARISON_DRILLDOWN",
            StatV1DataComparisonDrilldownGETSchema.class,
            "/stat/v1/global/comparison/drilldown");

    /* Отчет товары и заказы */

    public static final RequestType<StatV1DataGETSchema> ECOMMERCE_ORDERS_TABLE = report(
            "ECOMMERCE_ORDERS_TABLE",
            StatV1DataGETSchema.class,
            "/stat/v1/custom/ecommerce_orders");

    public static final RequestType<StatV1DataDrilldownGETSchema> ECOMMERCE_ORDERS_DRILLDOWN = report(
            "ECOMMERCE_ORDERS_DRILLDOWN",
            StatV1DataDrilldownGETSchema.class,
            "/stat/v1/custom/ecommerce_orders/drilldown");

    /* Legacy-отчеты */

    public static final RequestType<StatV1DataGETSchema> LEGACY_TABLE = report(
            "LEGACY_TABLE",
            StatV1DataGETSchema.class,
            "/internal/metrage/stat/v1/data");

    public static final RequestType<StatV1DataDrilldownGETSchema> LEGACY_DRILLDOWN = report(
            "LEGACY_DRILLDOWN",
            StatV1DataDrilldownGETSchema.class,
            "/internal/metrage/stat/v1/data/drilldown");

    public static final RequestType<StatV1DataBytimeGETSchema> LEGACY_BY_TIME = report(
            "LEGACY_BY_TIME",
            StatV1DataBytimeGETSchema.class,
            "/internal/metrage/stat/v1/data/bytime");

    // грид посетителей

    public static final RequestType<StatV1UserListGETSchema> VISITORS_GRID = report(
            "VISITORS_GRID",
            StatV1UserListGETSchema.class,
            "/stat/v1/user/list"
    );

    public static final RequestType<StatV1UserInfoGETSchema> VISITOR_INFO = report(
            "VISITOR_INFO",
            StatV1UserInfoGETSchema.class,
            "/stat/v1/user/info"
    );

    public static final RequestType<StatV1UserVisitsGETSchema> VISITOR_VISITS = report(
            "VISITOR_VISITS",
            StatV1UserVisitsGETSchema.class,
            "/stat/v1/user/visits"
    );

    public static final RequestType<ManagementV1UserCommentsPOSTSchema> VISITOR_COMMENT = report(
            "VISITOR_COMMENT",
            ManagementV1UserCommentsPOSTSchema.class,
            "/management/v1/user/comments"
    );

    /* Конверсии */

    public static final RequestType<StatV1DataGETSchema> CONVERSION_RATE = report(
            "CONVERSION_RATE",
            StatV1DataGETSchema.class,
            "/stat/v1/data/conversion_rate");

    /* GA */

    public static final RequestType<AnalyticsV3DataGaGETSchema> ANALYTICS = report(
            "ANALYTICS",
            AnalyticsV3DataGaGETSchema.class,
            "/analytics/v3/data/ga");

    public static final RequestType<StatV1DataGETSchema> OFFLINE_CALLS = report(
            "OFFLINE_CALLS",
            StatV1DataGETSchema.class,
            "/stat/v1/custom/offline_calls/log");

    public static final RequestType<StatV1CustomMonitoringLogGETSchema> MONITORING_LOG = report(
            "MONITORING_LOG",
            StatV1CustomMonitoringLogGETSchema.class,
            "/stat/v1/custom/monitoring/log");

    /* Activity */
    public static final RequestType<StatV1DataVisitsByProtocolGETSchema> VISITS_BY_PROTOCOL = report(
            "VISITS_BY_PROTOCOL",
            StatV1DataVisitsByProtocolGETSchema.class,
            "/stat/v1/data/visits_by_protocol"
    );

    /*  Отчет паблишеры */
    public static RequestType<StatV1CustomPublishersLastVisitSchema> addCounterToPublishersLastVisitSchema(Long counterID) {
        return RequestType.report(
                "PUBLISHERS_LAST_VISIT",
                StatV1CustomPublishersLastVisitSchema.class,
                String.format("/internal/stat/v1/custom/publishers/last_visit/%d", counterID));
    }
}
