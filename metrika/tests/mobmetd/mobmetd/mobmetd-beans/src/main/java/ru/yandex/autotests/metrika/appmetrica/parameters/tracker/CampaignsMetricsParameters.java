package ru.yandex.autotests.metrika.appmetrica.parameters.tracker;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

import java.util.List;
import java.util.stream.Collectors;

/**
 * @author dancingelf
 */
public class CampaignsMetricsParameters extends AbstractFormParameters {

    @FormParameter("tracking_ids")
    private String trackingIds;

    @FormParameter("uid")
    private Long uid;

    public String getTrackingIds() {
        return trackingIds;
    }

    public Long getUid() {
        return uid;
    }

    public CampaignsMetricsParameters withTrackingIds(List<String> trackingIds) {
        this.trackingIds = trackingIds.stream().collect(Collectors.joining(","));
        return this;
    }

    public CampaignsMetricsParameters withUid(Long uid) {
        this.uid = uid;
        return this;
    }
}
