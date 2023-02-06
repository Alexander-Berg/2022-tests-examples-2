package ru.yandex.autotests.mordabackend.utils.parameters;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesV122Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_V12_2;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;
import static ru.yandex.autotests.utils.morda.url.DomainManager.getMasterDomain;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16.07.14
 */
public class TabsParameterProvider implements ParameterProvider {

    public TabsParameterProvider() {
    }

    @Override
    public List<Object[]> getParams(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                    Language language, UserAgent userAgent) {

        List<Object[]> result = new ArrayList<>();
        List<ServicesV122Entry> servicesV12Entries = exports(SERVICES_V12_2,
                domain(userAgent.isMobile() && userAgent.getIsTouch() == 0 ? getMasterDomain(region.getDomain()) :  region.getDomain()),
                anyOf(having(on(ServicesV122Entry.class).getTabs(), not(equalTo(0))),
                        having(on(ServicesV122Entry.class).getTabsMore(), not(equalTo(0)))
                )
        );
        for (ServicesV122Entry entry : servicesV12Entries) {
            result.add(new Object[]{entry.getId(), entry});
        }

        return result;
    }
}
