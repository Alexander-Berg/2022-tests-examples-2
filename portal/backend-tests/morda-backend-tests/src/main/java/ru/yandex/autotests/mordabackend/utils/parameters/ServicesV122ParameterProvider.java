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
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_V12_2;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.export;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16.07.14
 */
public class ServicesV122ParameterProvider implements ParameterProvider {
    private String serviceId;

    public ServicesV122ParameterProvider(String serviceId) {
        this.serviceId = serviceId;
    }

    @Override
    public List<Object[]> getParams(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                    Language language, UserAgent userAgent) {

        List<Object[]> result = new ArrayList<>();
        ServicesV122Entry servicesV122Entry = export(SERVICES_V12_2, domain(region.getDomain()),
                having(on(ServicesV122Entry.class).getId(), equalTo(serviceId)));
        result.add(new Object[]{servicesV122Entry});

        return result;
    }
}
