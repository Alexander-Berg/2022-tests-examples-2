package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * Created by graev on 12/04/2017.
 */
public class TSEventParameters extends AbstractFormParameters {

    @FormParameter("appId")
    private Long appId;

    @FormParameter("mask")
    private String mask;

    @FormParameter("offset")
    private Integer offset;

    @FormParameter("limit")
    private Integer limit;

    public Long getAppId() {
        return appId;
    }

    public void setAppId(Long appId) {
        this.appId = appId;
    }

    public String getMask() {
        return mask;
    }

    public void setMask(String mask) {
        this.mask = mask;
    }

    public Integer getOffset() {
        return offset;
    }

    public void setOffset(Integer offset) {
        this.offset = offset;
    }

    public Integer getLimit() {
        return limit;
    }

    public void setLimit(Integer limit) {
        this.limit = limit;
    }

    public TSEventParameters withAppId(Long appId) {
        this.appId = appId;
        return this;
    }

    public TSEventParameters withMask(String mask) {
        this.mask = mask;
        return this;
    }

    public TSEventParameters withOffset(Integer offset) {
        this.offset = offset;
        return this;
    }

    public TSEventParameters withLimit(Integer limit) {
        this.limit = limit;
        return this;
    }

}
