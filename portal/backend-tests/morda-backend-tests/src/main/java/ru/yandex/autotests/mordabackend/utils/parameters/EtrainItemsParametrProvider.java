package ru.yandex.autotests.mordabackend.utils.parameters;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.etrains.EtrainItem;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.List;

/**
 * User: ivannik
 * Date: 10.09.2014
 */
public class EtrainItemsParametrProvider implements ParameterProvider {

    @Override
    public List<Object[]> getParams(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                    Language language, UserAgent userAgent) {
        List<EtrainItem> itemsList = new ArrayList<>();
        itemsList.addAll(cleanvars.getEtrains().getFctd());
        itemsList.addAll(cleanvars.getEtrains().getFctm());
        itemsList.addAll(cleanvars.getEtrains().getTctd());
        itemsList.addAll(cleanvars.getEtrains().getTctm());
        List<Object[]> data = new ArrayList<>();
        for (EtrainItem item : itemsList) {
            data.add(new Object[]{item.getTime(), item});
        }
        return data;
    }
}
