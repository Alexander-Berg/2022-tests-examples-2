package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class LogRequestParameters extends AbstractFormParameters {

    @FormParameter("date1")
    private String date1;

    @FormParameter("date2")
    private String date2;

    @FormParameter("source")
    private String source;

    @FormParameter("fields")
    private String fields;

    public String getDate1() {
        return date1;
    }

    public void setDate1(String date1) {
        this.date1 = date1;
    }

    public LogRequestParameters withDate1(String date1) {
        this.date1 = date1;
        return this;
    }

    public String getDate2() {
        return date2;
    }

    public void setDate2(String date2) {
        this.date2 = date2;
    }

    public LogRequestParameters withDate2(String date2) {
        this.date2 = date2;
        return this;
    }

    public String getSource() {
        return source;
    }

    public void setSource(String source) {
        this.source = source;
    }

    public LogRequestParameters withSource(String source) {
        this.source = source;
        return this;
    }

    public String getFields() {
        return fields;
    }

    public void setFields(String fields) {
        this.fields = fields;
    }

    public LogRequestParameters withFields(String fields) {
        this.fields = fields;
        return this;
    }
}
