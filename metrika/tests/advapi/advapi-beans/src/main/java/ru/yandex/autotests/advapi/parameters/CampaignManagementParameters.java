package ru.yandex.autotests.advapi.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class CampaignManagementParameters extends CommonParameters {

    @FormParameter("advertiser_id")
    private Integer advertiserId;

    @FormParameter("filter")
    private String filter;

    @FormParameter("from")
    private String from;

    @FormParameter("to")
    private String to;

    @FormParameter("status")
    private String status;

    @FormParameter("sort")
    private String sort;

    @FormParameter("override")
    private boolean override;

    public Integer getAdvertiserId() {
        return advertiserId;
    }

    public void setAdvertiserId(int advertiserId) {
        this.advertiserId = advertiserId;
    }

    public CampaignManagementParameters withAdvertiserId(long advertiserId) {
        this.advertiserId = (int) advertiserId;
        return this;
    }

    public String getFilter() {
        return filter;
    }

    public void setFilter(String filter) {
        this.filter = filter;
    }

    public CampaignManagementParameters withFilter(String filter) {
        this.filter = filter;
        return this;
    }

    public String getFrom() {
        return from;
    }

    public void setFrom(String from) {
        this.from = from;
    }

    public CampaignManagementParameters withFrom(String from) {
        this.from = from;
        return this;
    }

    public String getTo() {
        return to;
    }

    public void setTo(String to) {
        this.to = to;
    }

    public CampaignManagementParameters withTo(String to) {
        this.to = to;
        return this;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(CampaignStatus status) {
        this.status = status.name();
    }

    public CampaignManagementParameters withStatus(CampaignStatus status) {
        this.status = status.name();
        return this;
    }

    public CampaignManagementParameters withStatus(String status) {
        this.status = status;
        return this;
    }

    public String getSort() {
        return sort;
    }

    public void setSort(String sort) {
        this.sort = sort;
    }

    public CampaignManagementParameters withSort(CampaignsSort sort) {
        this.sort = sort.name();
        return this;
    }

    public CampaignManagementParameters withSort(String sort) {
        this.sort = sort;
        return this;
    }

    public boolean isOverride() {
        return override;
    }

    public void setOverride(boolean override) {
        this.override = override;
    }

    public CampaignManagementParameters withOverride(boolean override) {
        this.override = override;
        return this;
    }
}
