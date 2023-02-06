package ru.yandex.autotests.morda.data.exports;

import ru.yandex.autotests.morda.MordaPagesProperties;
import ru.yandex.autotests.morda.beans.exports.services_v12_2.ServicesV122Entry;
import ru.yandex.autotests.morda.beans.exports.services_v12_2.ServicesV122Export;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaDomain;

import static ru.yandex.autotests.morda.pages.main.DesktopMainMorda.desktopMain;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/06/16
 */
public class ServicesV12ExportProvider {
    private static final MordaPagesProperties PAGES_CONFIG = new MordaPagesProperties();
    private static final ServicesV122Export SERVICES_V_12_2 = new ServicesV122Export().populate(
            desktopMain(PAGES_CONFIG.getEnvironment()).getUrl()
    );

    public ServicesV122Entry getServicesV12Entry(String serviceId, MordaDomain domain) {
//        List<ServicesV122Entry> entries = SERVICES_V_12_2.getData().stream()
//                .filter(e -> serviceId.equals(e.getId()) && domain.equals(MordaDomain.fromString(e.getDomain())))
//                .collect(Collectors.toList());
//        assertThat("Must have only one entry", entries, hasSize(1));
        return null;
    }

    public ServicesV122Entry getServicesV12Entry(String serviceId, Morda<?> morda) {
        return getServicesV12Entry(serviceId, morda.getDomain());
    }

}
