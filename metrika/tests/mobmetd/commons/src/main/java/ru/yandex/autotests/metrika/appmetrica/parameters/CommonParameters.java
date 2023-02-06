package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Общие параметры всех запросов
 */
public class CommonParameters extends AbstractFormParameters {

    @FormParameter("internal_token")
    private String internalToken;

    @FormParameter("request_source")
    private String requestSource;

    @FormParameter("pretty")
    private String pretty = "true";

    @FormParameter("accuracy")
    private String defaultAccuracy;

    @FormParameter("uid_real")
    private String uidReal;

    public String getInternalToken() {
        return internalToken;
    }

    public void setInternalToken(String internalToken) {
        this.internalToken = internalToken;
    }

    public String getRequestSource() {
        return requestSource;
    }

    public void setRequestSource(String requestSource) {
        this.requestSource = requestSource;
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

    public String getUidReal() {
        return uidReal;
    }

    public void setUidReal(String uidReal) {
        this.uidReal = uidReal;
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

    public CommonParameters withInternalToken(final String internalToken) {
        this.internalToken = internalToken;
        return this;
    }

    public CommonParameters withDefaultAccuracy(final String defaultAccuracy) {
        this.defaultAccuracy = defaultAccuracy;
        return this;
    }

    public CommonParameters withUidReal(final String uidReal) {
        this.uidReal = uidReal;
        return this;
    }
}
