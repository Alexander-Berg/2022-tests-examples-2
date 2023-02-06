package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class CAReportParameters extends TableReportParameters {

    @FormParameter("group_method")
    public String groupMethod;

    @FormParameter("group")
    public String group;

    @FormParameter("brackets")
    public String brackets;

    /**
     * Параметр метрики
     */
    @FormParameter("event_name")
    public String eventName;

    /**
     * Параметр группировки
     */
    @FormParameter("url_parameter_key")
    public String urlParameterKey;

    /**
     * Параметр группировки
     */
    @FormParameter("url_parameter_key_1")
    public String urlParameterKey1;

    public String getGroupMethod() {
        return groupMethod;
    }

    public void setGroupMethod(String groupMethod) {
        this.groupMethod = groupMethod;
    }

    public String getGroup() {
        return group;
    }

    public void setGroup(String group) {
        this.group = group;
    }

    public String getBrackets() {
        return brackets;
    }

    public void setBrackets(String brackets) {
        this.brackets = brackets;
    }

    public String getUrlParameterKey() {
        return urlParameterKey;
    }

    public void setUrlParameterKey(String urlParameterKey) {
        this.urlParameterKey = urlParameterKey;
    }

    public String getUrlParameterKey1() {
        return urlParameterKey1;
    }

    public void setUrlParameterKey1(String urlParameterKey1) {
        this.urlParameterKey1 = urlParameterKey1;
    }

    public String getEventName() {
        return eventName;
    }

    public void setEventName(String eventName) {
        this.eventName = eventName;
    }

    public CAReportParameters withGroupMethod(String groupMethod) {
        this.groupMethod = groupMethod;
        return this;
    }

    public CAReportParameters withGroup(String group) {
        this.group = group;
        return this;
    }

    public CAReportParameters withBrackets(String brackets) {
        this.brackets = brackets;
        return this;
    }

    public CAReportParameters withEventName(String eventName) {
        this.eventName = eventName;
        return this;
    }

    public CAReportParameters withUrlParameterKey(String urlParameterKey) {
        this.urlParameterKey = urlParameterKey;
        return this;
    }

    public CAReportParameters withUrlParameterKey1(String urlParameterKey1) {
        this.urlParameterKey1 = urlParameterKey1;
        return this;
    }
}
