package ru.yandex.autotests.mordabackend.utils.parameters;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16.07.14
 */
public class EmptyParameterProvider implements ParameterProvider {
    @Override
    public List<Object[]> getParams(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                                    Region region, Language language, UserAgent userAgent) {
        return null;
    }
}
