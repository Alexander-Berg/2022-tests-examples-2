package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class CommonFrontParameters extends AbstractFormParameters {

    @FormParameter("lang")
    private String lang = "ru";

    @FormParameter("request_domain")
    private String requestDomain = "ru";

    @FormParameter("uid")
    private Long uid;

    public String getLang() {
        return lang;
    }

    public String getRequestDomain() {
        return requestDomain;
    }

    public Long getUid() {
        return uid;
    }

    public void setLang(String lang) {
        this.lang = lang;
    }

    public void setRequestDomain(String requestDomain) {
        this.requestDomain = requestDomain;
    }

    public void setUid(Long uid) {
        this.uid = uid;
    }

    public CommonFrontParameters withLang(String lang) {
        this.lang = lang;
        return this;
    }

    public CommonFrontParameters withRequestDomain(String requestDomain) {
        this.requestDomain = requestDomain;
        return this;
    }

    public CommonFrontParameters withUid(Long uid) {
        this.uid = uid;
        return this;
    }
}
