package ru.yandex.autotests.morda.data.topnews;

import ru.yandex.autotests.morda.beans.exports.services_v12_2.ServicesV122Entry;
import ru.yandex.autotests.morda.data.exports.ServicesV12ExportProvider;
import ru.yandex.autotests.morda.pages.Morda;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/06/16
 */
public interface TopnewsData {
    ServicesV12ExportProvider SERVICES_V_12_PROVIDER = new ServicesV12ExportProvider();

    static String getTopnewsHost(Morda<?> morda) {
        ServicesV122Entry servicesV122Entry = SERVICES_V_12_PROVIDER.getServicesV12Entry("news", morda);
        switch (morda.getMordaType().getContent()) {
            case MOB:
                return servicesV122Entry.getPda();
            case TOUCH:
                return servicesV122Entry.getTouch();
            default:
                return servicesV122Entry.getHref();
        }
    }

}
