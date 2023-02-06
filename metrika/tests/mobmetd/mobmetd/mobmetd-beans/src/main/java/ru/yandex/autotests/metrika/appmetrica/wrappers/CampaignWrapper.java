package ru.yandex.autotests.metrika.appmetrica.wrappers;

import ru.yandex.metrika.mobmet.model.redirect.Campaign;

/**
 * Created by graev on 13/12/2016.
 */
public final class CampaignWrapper {

    private Campaign campaign;

    public static CampaignWrapper wrap(Campaign campaign) {
        return new CampaignWrapper(campaign);
    }

    public CampaignWrapper(Campaign campaign) {
        this.campaign = campaign;
    }

    public Campaign getCampaign() {
        return campaign;
    }

    @Override
    public String toString() {
        return campaign.getName();
    }
}
