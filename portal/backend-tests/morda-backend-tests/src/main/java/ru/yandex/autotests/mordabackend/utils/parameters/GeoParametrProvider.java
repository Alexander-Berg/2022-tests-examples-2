package ru.yandex.autotests.mordabackend.utils.parameters;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.geo.GeoItem;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static org.hamcrest.Matchers.isIn;

/**
 * User: ivannik
 * Date: 18.07.2014
 */
public class GeoParametrProvider implements ParameterProvider {

    private List<String> serviceIds;

    public GeoParametrProvider(String ... serviceIds) {
        this.serviceIds = Arrays.asList(serviceIds);
    }

    @Override
    public List<Object[]> getParams(MordaClient mordaClient, Client client, Cleanvars cleanvars, Region region,
                                    Language language, UserAgent userAgent) {
        List<GeoItem> itemsList = new ArrayList<>();
        itemsList.addAll(select(cleanvars.getGeo().getList(),
                having(on(GeoItem.class).getService(), isIn(serviceIds))));
        itemsList.addAll(select(cleanvars.getGeo().getListIcon(),
                having(on(GeoItem.class).getService(), isIn(serviceIds))));
        List<Object[]> data = new ArrayList<>();
        for (GeoItem geoItem : itemsList) {
            data.add(new Object[]{geoItem.getService(), geoItem});
        }
        return data;
    }
}
