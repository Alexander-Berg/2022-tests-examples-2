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
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.SERVICES_V12_2;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.DomainMatcher.domain;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16.07.14
 */
public class ServicesParameterProvider implements ParameterProvider {
    private Morda morda;

    public ServicesParameterProvider(Morda morda) {
        this.morda = morda;
    }

    @Override
    public List<Object[]> getParams(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                    Language language, UserAgent userAgent) {

        List<ServicesV122Entry> entries;
        if (morda.equals(Morda.TOUCH)) {
            entries = getTouchServices(region, language, userAgent);
        } else {
            entries = new ArrayList<>();
        }

        List<Object[]> result = new ArrayList<>();

        for (ServicesV122Entry entry : entries) {
            result.add(new Object[]{entry.getId(), entry});
        }

        return result;
    }

    public static List<ServicesV122Entry> getBigServices() {
        return new ArrayList<>();
    }

    public static List<ServicesV122Entry> getTouchServices(Region region, Language language, UserAgent userAgent) {
        return exports(SERVICES_V12_2, domain(region.getDomain()),
                having(on(ServicesV122Entry.class).getMobMorda(), not(equalTo(0))),
                having(on(ServicesV122Entry.class).getDisabled(), isEmptyOrNullString()));
    }

    public enum Morda {
        BIG,
        TOUCH,
        MOB
    }
}
