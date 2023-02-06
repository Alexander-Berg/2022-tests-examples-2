package ru.yandex.autotests.metrika.data.parameters.management.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.metrika.api.management.client.external.logs.LogRequestSource;

public class LogsApiParameters extends AbstractFormParameters {
    @FormParameter("date1")
    private String date1;
    @FormParameter("date2")
    private String date2;
    @FormParameter("source")
    private LogRequestSource source;
    @FormParameter("fields")
    private String fields;

    public LogsApiParameters(String date1, String date2, LogRequestSource source, String fields) {
        this.date1 = date1;
        this.date2 = date2;
        this.source = source;
        this.fields = fields;
    }

    public String getDate1() {
        return date1;
    }

    public void setDate1(String date1) {
        this.date1 = date1;
    }

    public LogsApiParameters withDate1(String date1) {
        setDate1(date1);
        return this;
    }

    public String getDate2() {
        return date2;
    }

    public void setDate2(String date2) {
        this.date2 = date2;
    }

    public LogsApiParameters withDate2(String date2) {
        setDate2(date2);
        return this;
    }


    public LogRequestSource getSource() {
        return source;
    }

    public void setSource(LogRequestSource source) {
        this.source = source;
    }

    public LogsApiParameters withSource(LogRequestSource source) {
        setSource(source);
        return this;
    }

    public String getFields() {
        return fields;
    }

    public void setFields(String fields) {
        this.fields = fields;
    }

    public LogsApiParameters withFields(String fields) {
        setFields(fields);
        return this;
    }
}
