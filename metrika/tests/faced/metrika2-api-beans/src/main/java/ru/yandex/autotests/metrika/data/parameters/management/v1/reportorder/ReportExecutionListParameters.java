package ru.yandex.autotests.metrika.data.parameters.management.v1.reportorder;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;

/**
 * @author zgmnkv
 */
public class ReportExecutionListParameters extends AbstractFormParameters {

    @FormParameter("offset")
    private Integer offset;

    @FormParameter("limit")
    private Integer limit;

    public Integer getOffset() {
        return offset;
    }

    public void setOffset(Integer offset) {
        this.offset = offset;
    }

    public ReportExecutionListParameters withOffset(Integer offset) {
        this.offset = offset;
        return this;
    }

    public Integer getLimit() {
        return limit;
    }

    public void setLimit(Integer limit) {
        this.limit = limit;
    }

    public ReportExecutionListParameters withLimit(Integer limit) {
        this.limit = limit;
        return this;
    }
}
