package ru.yandex.autotests.metrika.appmetrica.wrappers;

import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;

/**
 * Created by graev on 22/12/2016.
 */
public final class PartnerWrapper {
    public final TrackingPartner partner;

    public static PartnerWrapper wrap(TrackingPartner partner) {
        return new PartnerWrapper(partner);
    }

    public PartnerWrapper(TrackingPartner partner) {
        this.partner = partner;
    }

    public TrackingPartner getPartner() {
        return partner;
    }

    @Override
    public String toString() {
        return partner.getName();
    }
}
