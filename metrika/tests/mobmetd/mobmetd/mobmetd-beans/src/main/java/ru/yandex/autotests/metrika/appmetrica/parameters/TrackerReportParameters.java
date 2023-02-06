package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Параметры получения списка трекеров
 *
 * @author dancingelf
 */
public class TrackerReportParameters extends CommonReportParameters {

    @FormParameter("app_id")
    private Long appId;

    @FormParameter("uid")
    private Long uid;

    public Long getAppId() {
        return appId;
    }

    public void setAppId(Long appId) {
        this.appId = appId;
    }

    public Long getUid() {
        return uid;
    }

    public void setUid(Long uid) {
        this.uid = uid;
    }

    public TrackerReportParameters withAppId(Long appId) {
        setAppId(appId);
        return this;
    }

    public TrackerReportParameters withUid(Long uid) {
        setUid(uid);
        return this;
    }
}
