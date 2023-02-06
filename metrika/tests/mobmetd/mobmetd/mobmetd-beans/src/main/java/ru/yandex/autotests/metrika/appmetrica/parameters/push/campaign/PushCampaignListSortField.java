package ru.yandex.autotests.metrika.appmetrica.parameters.push.campaign;

import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignBriefAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.model.CampaignStatus;

import java.util.Comparator;

public enum PushCampaignListSortField {

    date(Comparator.comparing(PushCampaignBriefAdapter::getCreationTime)),
    name(Comparator.comparing(PushCampaignBriefAdapter::getName)),
    author(Comparator.comparing(PushCampaignBriefAdapter::getOwnerUid)),
    status(Comparator.comparing(PushCampaignBriefAdapter::getStatus, Comparator.nullsFirst(Comparator.comparingInt(CampaignStatus::ordinal))));

    private final Comparator<PushCampaignBriefAdapter> comparator;

    PushCampaignListSortField(Comparator<PushCampaignBriefAdapter> comparator) {
        this.comparator = comparator;
    }

    public Comparator<PushCampaignBriefAdapter> getComparator() {
        return comparator;
    }
}
