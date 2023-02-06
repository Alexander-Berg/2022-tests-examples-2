package ru.yandex.autotests.mordabackend.utils.parameters;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordaexportsclient.beans.ServicesTabsEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_TABS;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16.07.14
 */
public class ServicesTabsParameterProvider implements ParameterProvider {

    private final String content;

    public ServicesTabsParameterProvider(String content) {
        this.content = content;
    }

    @Override
    public List<Object[]> getParams(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                    Language language, UserAgent userAgent) {

        List<Object[]> result = new ArrayList<>();
        List<ServicesTabsEntry> servicesTabsEntries = exports(SERVICES_TABS, domain(region.getDomain()),
                having(on(ServicesTabsEntry.class).getContent(), equalTo(content)),
                having(on(ServicesTabsEntry.class).getTabs(), not(isEmptyOrNullString())));
        for (ServicesTabsEntry entry : servicesTabsEntries) {
            result.add(new Object[]{entry.getId(), entry});
        }

        return result;
    }
}
