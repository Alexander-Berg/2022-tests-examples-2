package ru.yandex.autotests.metrika.data.parameters.management.v1.reportorder;

import ru.yandex.autotests.httpclient.lite.core.AbstractFormParameters;
import ru.yandex.autotests.httpclient.lite.core.FormParameter;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderStatus;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderType;

/**
 * @author zgmnkv
 */
public class ReportOrderListParameters extends AbstractFormParameters {

    @FormParameter("type")
    private ReportOrderType type;

    @FormParameter("status")
    private ReportOrderStatus status;

    @FormParameter("offset")
    private Integer offset;

    @FormParameter("limit")
    private Integer limit;

    @FormParameter("sort_type")
    private ReportOrderListSortType sortType;

    public ReportOrderType getType() {
        return type;
    }

    public void setType(ReportOrderType type) {
        this.type = type;
    }

    public ReportOrderListParameters withType(ReportOrderType type) {
        this.type = type;
        return this;
    }

    public ReportOrderStatus getStatus() {
        return status;
    }

    public void setStatus(ReportOrderStatus status) {
        this.status = status;
    }

    public ReportOrderListParameters withStatus(ReportOrderStatus status) {
        this.status = status;
        return this;
    }

    public Integer getOffset() {
        return offset;
    }

    public void setOffset(Integer offset) {
        this.offset = offset;
    }

    public ReportOrderListParameters withOffset(Integer offset) {
        this.offset = offset;
        return this;
    }

    public Integer getLimit() {
        return limit;
    }

    public void setLimit(Integer limit) {
        this.limit = limit;
    }

    public ReportOrderListParameters withLimit(Integer limit) {
        this.limit = limit;
        return this;
    }

    public ReportOrderListSortType getSortType() {
        return sortType;
    }

    public void setSortType(ReportOrderListSortType sortType) {
        this.sortType = sortType;
    }

    public ReportOrderListParameters withSortType(ReportOrderListSortType sortType) {
        this.sortType = sortType;
        return this;
    }
}
