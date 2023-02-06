package ru.yandex.autotests.metrika.data.parameters.report.v1;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class MonitoringLogParameters extends AbstractFormParameters {

    @FormParameter("id")
    private Long id;

    @FormParameter("date1")
    private String date1;

    @FormParameter("date2")
    private String date2;

    @FormParameter("filter")
    private String filter;

    @FormParameter("reverse")
    private Boolean reverse;

    @FormParameter("offset")
    private Integer offset;

    @FormParameter("per_page")
    private Integer perPage;

    @FormParameter("lang")
    private String lang;

    @FormParameter("pretty")
    private boolean pretty;

    @FormParameter("mirror_id")
    private String mirrorId;

    @FormParameter("sort")
    private String sort;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public MonitoringLogParameters withId(Long id) {
        this.id = id;
        return this;
    }

    public String getDate1() {
        return date1;
    }

    public void setDate1(String date1) {
        this.date1 = date1;
    }

    public MonitoringLogParameters withDate1(String date1) {
        this.date1 = date1;
        return this;
    }

    public String getDate2() {
        return date2;
    }

    public void setDate2(String date2) {
        this.date2 = date2;
    }

    public MonitoringLogParameters withDate2(String date2) {
        this.date2 = date2;
        return this;
    }

    public String getFilter() {
        return filter;
    }

    public void setFilter(String filter) {
        this.filter = filter;
    }

    public MonitoringLogParameters withFilter(String filter) {
        this.filter = filter;
        return this;
    }

    public Boolean getReverse() {
        return reverse;
    }

    public void setReverse(Boolean reverse) {
        this.reverse = reverse;
    }

    public MonitoringLogParameters withReverse(Boolean reverse) {
        this.reverse = reverse;
        return this;
    }

    public Integer getOffset() {
        return offset;
    }

    public void setOffset(Integer offset) {
        this.offset = offset;
    }

    public MonitoringLogParameters withOffset(Integer offset) {
        this.offset = offset;
        return this;
    }

    public Integer getPerPage() {
        return perPage;
    }

    public void setPerPage(Integer perPage) {
        this.perPage = perPage;
    }

    public MonitoringLogParameters withPerPage(Integer perPage) {
        this.perPage = perPage;
        return this;
    }

    public String getLang() {
        return lang;
    }

    public void setLang(String lang) {
        this.lang = lang;
    }

    public MonitoringLogParameters withLang(String lang) {
        this.lang = lang;
        return this;
    }

    public boolean isPretty() {
        return pretty;
    }

    public void setPretty(boolean pretty) {
        this.pretty = pretty;
    }

    public MonitoringLogParameters withPretty(boolean pretty) {
        this.pretty = pretty;
        return this;
    }

    public String getMirrorId() {
        return mirrorId;
    }

    public void setMirrorId(String mirrorId) {
        this.mirrorId = mirrorId;
    }

    public MonitoringLogParameters withMirrorId(String mirrorId) {
        this.mirrorId = mirrorId;
        return this;
    }

    public String getSort() {
        return sort;
    }

    public void setSort(String sort) {
        this.sort = sort;
    }

    public MonitoringLogParameters withSort(String sort) {
        this.sort = sort;
        return this;
    }
}
