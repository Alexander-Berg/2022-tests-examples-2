package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class StackTraceReportParameters extends CommonFrontParameters {

    @FormParameter("app_id")
    private Long appId;

    @FormParameter("date")
    private String date;

    @FormParameter("device_id")
    private String deviceId;

    @FormParameter("event_id")
    private String eventId;

    @FormParameter("url")
    private String url;

    public Long getAppId() {
        return appId;
    }

    public StackTraceReportParameters withAppId(Long appId) {
        this.appId = appId;
        return this;
    }

    public String getDate() {
        return date;
    }

    public StackTraceReportParameters withDate(String date) {
        this.date = date;
        return this;
    }

    public String getDeviceId() {
        return deviceId;
    }

    public StackTraceReportParameters withDeviceId(String deviceId) {
        this.deviceId = deviceId;
        return this;
    }

    public String getEventId() {
        return eventId;
    }

    public StackTraceReportParameters withEventId(String eventId) {
        this.eventId = eventId;
        return this;
    }

    public String getUrl() {
        return url;
    }

    public StackTraceReportParameters withUrl(String url) {
        this.url = url;
        return this;
    }
}
