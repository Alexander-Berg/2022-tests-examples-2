package ru.yandex.autotests.metrika.data.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.autotests.metrika.data.common.users.User;

/**
 * Общие параметры всех запросов
 * <p>
 * Created by konkov on 21.07.2015.
 */
public class CommonParameters extends AbstractFormParameters {

    @FormParameter("request_source")
    private String requestSource;

    @FormParameter("request_domain")
    private String requestDomain;

    @FormParameter("pretty")
    private String pretty = "true";

    @FormParameter("accuracy")
    private String defaultAccuracy;

    @FormParameter("uid")
    private Long uid;

    @FormParameter("lang")
    private String lang;

    public String getRequestSource() {
        return requestSource;
    }

    public void setRequestSource(String requestSource) {
        this.requestSource = requestSource;
    }

    public String getRequestDomain() {
        return requestDomain;
    }

    public void setRequestDomain(String requestDomain) {
        this.requestDomain = requestDomain;
    }

    public String getPretty() {
        return pretty;
    }

    public void setPretty(String pretty) {
        this.pretty = pretty;
    }

    public void setPretty(boolean pretty) {
        this.pretty = String.valueOf(pretty);
    }

    public String getDefaultAccuracy() {
        return defaultAccuracy;
    }

    public void setDefaultAccuracy(String defaultAccuracy) {
        this.defaultAccuracy = defaultAccuracy;
    }

    public Long getUid() {
        return uid;
    }

    public void setUid(Long uid) {
        this.uid = uid;
    }

    public void setUid(User user) {
        setUid(user.get(User.UID));
    }

    public String getLang() {
        return lang;
    }

    public void setLang(String lang) {
        this.lang = lang;
    }

    public CommonParameters withPretty(final String pretty) {
        this.pretty = pretty;
        return this;
    }

    public CommonParameters withPretty(final boolean pretty) {
        this.pretty = String.valueOf(pretty);
        return this;
    }

    public CommonParameters withRequestSource(final String requestSource) {
        this.requestSource = requestSource;
        return this;
    }

    public CommonParameters withRequestDomain(final String requestDomain) {
        this.requestDomain = requestDomain;
        return this;
    }

    public CommonParameters withDefaultAccuracy(final String defaultAccuracy) {
        this.defaultAccuracy = defaultAccuracy;
        return this;
    }

    public CommonParameters withUid(final Long uid) {
        this.uid = uid;
        return this;
    }

    public CommonParameters withUid(User user) {
        return withUid(user.get(user.UID));
    }

    public CommonParameters withLang(String lang) {
        this.lang = lang;
        return this;
    }
}
