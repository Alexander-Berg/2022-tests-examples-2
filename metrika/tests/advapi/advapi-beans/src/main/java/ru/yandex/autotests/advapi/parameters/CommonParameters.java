package ru.yandex.autotests.advapi.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class CommonParameters extends AbstractFormParameters {

    @FormParameter("pretty")
    private String pretty = "true";

    @FormParameter("lang")
    private String lang;

    @FormParameter("limit")
    private Integer limit;

    @FormParameter("offset")
    private Integer offset;

    @FormParameter("uid_real")
    private Long uidReal;

    @FormParameter("uid")
    private Long uid;

    @FormParameter("reversed")
    private Boolean reversed;

    @FormParameter("accuracy")
    private String defaultAccuracy;

    @FormParameter("table")
    private String table;

    public String getPretty() {
        return pretty;
    }

    public void setPretty(String pretty) {
        this.pretty = pretty;
    }

    public CommonParameters withPretty(String pretty) {
        this.pretty = pretty;
        return this;
    }

    public String getLang() {
        return lang;
    }

    public void setLang(String lang) {
        this.lang = lang;
    }

    public CommonParameters withLang(String lang) {
        this.lang = lang;
        return this;
    }

    public Integer getLimit() {
        return limit;
    }

    public void setLimit(Integer limit) {
        this.limit = limit;
    }

    public CommonParameters withLimit(Integer limit) {
        this.limit = limit;
        return this;
    }

    public Integer getOffset() {
        return offset;
    }

    public void setOffset(Integer offset) {
        this.offset = offset;
    }

    public CommonParameters withOffset(Integer offset) {
        this.offset = offset;
        return this;
    }

    public Long getUidReal() {
        return uidReal;
    }

    public void setUidReal(Long uidReal) {
        this.uidReal = uidReal;
    }

    public CommonParameters withUidReal(Long uidReal) {
        this.uidReal = uidReal;
        return this;
    }

    public Boolean getReversed() {
        return reversed;
    }

    public void setReversed(Boolean reversed) {
        this.reversed = reversed;
    }

    public CommonParameters withReversed(Boolean reversed) {
        this.reversed = reversed;
        return this;
    }

    public Long getUid() {
        return uid;
    }

    public void setUid(Long uid) {
        this.uid = uid;
    }

    public CommonParameters withUid(Long uid) {
        this.uid = uid;
        return this;
    }

    public String getDefaultAccuracy() {
        return defaultAccuracy;
    }

    public void setDefaultAccuracy(String defaultAccuracy) {
        this.defaultAccuracy = defaultAccuracy;
    }

    public CommonParameters withDefaultAccuracy(String defaultAccuracy) {
        this.defaultAccuracy = defaultAccuracy;
        return this;
    }

    public String getTable() {
        return table;
    }

    public void setTable(String table) {
        this.table = table;
    }

    public CommonParameters withTable(String table) {
        this.table = table;
        return this;
    }
}
