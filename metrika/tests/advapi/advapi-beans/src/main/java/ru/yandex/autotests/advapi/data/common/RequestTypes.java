package ru.yandex.autotests.advapi.data.common;

import ru.yandex.advapi.V1StatDataBytimeGETSchema;
import ru.yandex.advapi.V1StatDataDrilldownGETSchema;
import ru.yandex.advapi.V1StatDataGETSchema;

import static ru.yandex.autotests.advapi.data.common.RequestType.report;

/**
 * Created by konkov on 13.07.2016.
 */
public final class RequestTypes {

    private RequestTypes() {
    }

    public static final RequestType<V1StatDataGETSchema> TABLE = report(
            "TABLE",
            V1StatDataGETSchema.class,
            "/v1/stat/data");

    public static final RequestType<V1StatDataDrilldownGETSchema> DRILLDOWN = report(
            "DRILLDOWN",
            V1StatDataDrilldownGETSchema.class,
            "/v1/stat/data/drilldown");

    public static final RequestType<V1StatDataBytimeGETSchema> BY_TIME = report(
            "BY_TIME",
            V1StatDataBytimeGETSchema.class,
            "/v1/stat/data/bytime");
}
