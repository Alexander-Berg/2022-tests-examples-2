package ru.yandex.autotests.metrika.appmetrica.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class PushCampaignsListParameters extends CommonFrontParameters {
    @FormParameter("app_id")
    private Long appId;

    @FormParameter("offset")
    private Integer offset;

    @FormParameter("limit")
    private Integer limit;

    @FormParameter("include_push_api")
    private Boolean includePushApi;

    @FormParameter("sort")
    private String sort;

    @FormParameter("sort_order")
    private String sortOrder;

    @FormParameter("mask")
    private String mask;

    @FormParameter("uid")
    private Long uid;

    public long getAppId() {
        return appId;
    }

    public PushCampaignsListParameters withAppId(long appId) {
        this.appId = appId;
        return this;
    }

    public int getOffset() {
        return offset;
    }

    public PushCampaignsListParameters withOffset(int offset) {
        this.offset = offset;
        return this;
    }

    public int getLimit() {
        return limit;
    }

    public PushCampaignsListParameters withLimit(int limit) {
        this.limit = limit;
        return this;
    }

    public boolean isIncludePushApi() {
        return includePushApi;
    }

    public PushCampaignsListParameters withIncludePushApi(boolean includePushApi) {
        this.includePushApi = includePushApi;
        return this;
    }

    public String getSort() {
        return sort;
    }

    public PushCampaignsListParameters withSort(String sort) {
        this.sort = sort;
        return this;
    }

    public String getSortOrder() {
        return sortOrder;
    }

    public PushCampaignsListParameters withSortOrder(String sortOrder) {
        this.sortOrder = sortOrder;
        return this;
    }

    public String getMask() {
        return mask;
    }

    public PushCampaignsListParameters withMask(String mask) {
        this.mask = mask;
        return this;
    }

    public Long getUid() {
        return uid;
    }

    public PushCampaignsListParameters withUid(Long uid) {
        this.uid = uid;
        return this;
    }
}
