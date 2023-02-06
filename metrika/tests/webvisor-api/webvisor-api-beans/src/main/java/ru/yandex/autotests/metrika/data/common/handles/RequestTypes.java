package ru.yandex.autotests.metrika.data.common.handles;

import ru.yandex.autotests.metrika.beans.schemes.*;

import static ru.yandex.autotests.metrika.data.common.handles.RequestType.report;

/**
 * Created by konkov on 13.07.2016.
 */
public final class RequestTypes {
    private RequestTypes() {}

    public static final RequestType<StatV1DataGETSchema> TABLE = report(
            "TABLE",
            StatV1DataGETSchema.class,
            "/stat/v1/data");

    /* веб-визор */
    public static final RequestType<WebvisorV2DataVisitsGETSchema> WEBVISOR_VISITS_GRID = report(
            "WEBVISOR_VISITS_GRID",
            WebvisorV2DataVisitsGETSchema.class,
            "/webvisor/v2/data/visits");

    public static final RequestType<WebvisorV2DataHitsGETSchema> WEBVISOR_HITS_GRID = report(
            "WEBVISOR_HITS_GRID",
            WebvisorV2DataHitsGETSchema.class,
            "/webvisor/v2/data/hits");
    /* In-page аналитика */

    public static final RequestType<MapsV1DataLinkGETSchema> INPAGE_LINK_URLS = report(
            "INPAGE_LINK_URLS",
            MapsV1DataLinkGETSchema.class,
            "/maps/v1/data/link");

    public static final RequestType<MapsV1DataFormGETPOSTSchema> INPAGE_FORM = report(
            "INPAGE_FORM",
            MapsV1DataFormGETPOSTSchema.class,
            "/maps/v1/data/form");

    public static final RequestType<MapsV1DataLinkMapGETSchema> INPAGE_LINK = report(
            "INPAGE_LINK",
            MapsV1DataLinkMapGETSchema.class,
            "/maps/v1/data/link/map");

    public static final RequestType<MapsV1DataClickGETSchema> INPAGE_CLICK = report(
            "INPAGE_CLICK",
            MapsV1DataClickGETSchema.class,
            "/maps/v1/data/click");

    public static final RequestType<MapsV1DataScrollGETSchema> INPAGE_SCROLL = report(
            "INPAGE_SCROLL",
            MapsV1DataScrollGETSchema.class,
            "/maps/v1/data/scroll");

}
