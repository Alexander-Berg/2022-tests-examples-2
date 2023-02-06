package ru.yandex.autotests.metrika.appmetrica.parameters.skad;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.metrika.segments.apps.misc.SKAdCVModelType;


public class SKAdCVParameters extends AbstractFormParameters {

    @FormParameter("app_id")
    private Long appId;

    @FormParameter("model")
    private SKAdCVModelType model;

    @FormParameter("date1")
    private String date1;

    @FormParameter("date2")
    private String date2;

    public Long getAppId() {
        return appId;
    }

    public void setAppId(Long appId) {
        this.appId = appId;
    }

    public SKAdCVParameters withAppId(Long appId) {
        this.appId = appId;
        return this;
    }

    public SKAdCVModelType getModel() {
        return model;
    }

    public void setModel(SKAdCVModelType model) {
        this.model = model;
    }

    public SKAdCVParameters withModel(SKAdCVModelType model) {
        this.model = model;
        return this;
    }

    public String getDate1() {
        return date1;
    }

    public void setDate1(String date1) {
        this.date1 = date1;
    }

    public SKAdCVParameters withDate1(String date1) {
        this.date1 = date1;
        return this;
    }

    public String getDate2() {
        return date2;
    }

    public void setDate2(String date2) {
        this.date2 = date2;
    }

    public SKAdCVParameters withDate2(String date2) {
        this.date2 = date2;
        return this;
    }
}
