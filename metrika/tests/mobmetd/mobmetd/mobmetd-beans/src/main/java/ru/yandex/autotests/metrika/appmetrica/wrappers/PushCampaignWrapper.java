package ru.yandex.autotests.metrika.appmetrica.wrappers;

import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignAdapter;

/**
 * Created by graev on 20/12/2016.
 */
public final class PushCampaignWrapper {
    private PushCampaignAdapter campaign;

    public static PushCampaignWrapper wrap(PushCampaignAdapter campaign) {
        return new PushCampaignWrapper(campaign);
    }

    public PushCampaignWrapper(PushCampaignAdapter campaign) {
        this.campaign = campaign;
    }

    public PushCampaignAdapter getCampaign() {
        return campaign;
    }

    @Override
    public String toString() {
        return campaign.getName();
    }
}
