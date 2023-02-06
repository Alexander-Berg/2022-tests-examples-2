package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class CloudExportRequestParams extends CommonFrontParameters {
    @FormParameter("export_type")
    private String type = "continuous";

    @FormParameter("offset")
    private int offset = 0;

    @FormParameter("limit")
    private int limit = 100;

    @FormParameter("sort")
    private String sort = "create_time";

    @FormParameter("sort_order")
    private String sortOrder = "asc";

    public String getType() {
        return type;
    }

    public CloudExportRequestParams withType(String type) {
        this.type = type;
        return this;
    }

    public int getOffset() {
        return offset;
    }

    public CloudExportRequestParams withOffset(int offset) {
        this.offset = offset;
        return this;
    }

    public int getLimit() {
        return limit;
    }

    public CloudExportRequestParams withLimit(int limit) {
        this.limit = limit;
        return this;
    }

    public String getSort() {
        return sort;
    }

    public CloudExportRequestParams withSort(String sort) {
        this.sort = sort;
        return this;
    }

    public String getSortOrder() {
        return sortOrder;
    }

    public CloudExportRequestParams withSortOrder(String sortOrder) {
        this.sortOrder = sortOrder;
        return this;
    }
}
