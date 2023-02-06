package ru.yandex.autotests.advapi.parameters;

import ru.yandex.autotests.httpclient.lite.core.FormParameter;

public class AdvertiserManagementParameters extends CommonParameters {

    @FormParameter("campaign_status")
    private String campaignStatus;

    public String getCampaignStatus() {
        return campaignStatus;
    }

    public void setCampaignStatus(String campaignStatus) {
        this.campaignStatus = campaignStatus;
    }

    public AdvertiserManagementParameters withCampaignStatus(CampaignStatus campaignStatus) {
        this.campaignStatus = campaignStatus.name();
        return this;
    }

    public AdvertiserManagementParameters withCampaignStatus(String campaignStatus) {
        this.campaignStatus = campaignStatus;
        return this;
    }
}
