package ru.yandex.autotests.metrika.appmetrica.parameters;

import java.util.List;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;

public final class UserAcquisitionParameters extends TableReportParameters {

    @FormParameter("events")
    private String events;

    @FormParameter("conversions")
    private String conversions;

    @FormParameter("loyaltyThreshold")
    private int loyaltyThreshold = 3;

    @FormParameter("source")
    private String source;

    public String getEvents() {
        return events;
    }

    public void setEvents(String events) {
        this.events = events;
    }

    public String getConversions() {
        return conversions;
    }

    public void setConversions(String conversions) {
        this.conversions = conversions;
    }

    public int getLoyaltyThreshold() {
        return loyaltyThreshold;
    }

    public void setLoyaltyThreshold(int loyaltyThreshold) {
        this.loyaltyThreshold = loyaltyThreshold;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public UserAcquisitionParameters withEvents(List<String> events) {
        this.events = JsonUtils.toString(events, true);
        return this;
    }

    public UserAcquisitionParameters withConversions(List<List<Long>> conversions) {
        this.conversions = JsonUtils.toString(conversions, true);
        return this;
    }

    public UserAcquisitionParameters withLoyaltyThreshold(int loyaltyThreshold) {
        this.loyaltyThreshold = loyaltyThreshold;
        return this;
    }

    public UserAcquisitionParameters withSource(TSSource source) {
        this.source = source.apiName();
        return this;
    }
}
