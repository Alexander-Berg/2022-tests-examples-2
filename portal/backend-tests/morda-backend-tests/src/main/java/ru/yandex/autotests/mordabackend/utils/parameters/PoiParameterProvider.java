package ru.yandex.autotests.mordabackend.utils.parameters;

import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.List;

/**
 * User: ivannik
 * Date: 22.08.2014
 */
public class PoiParameterProvider implements ParameterProvider {

    @Override
    public List<Object[]> getParams(MordaClient mordaClient, Client client, Cleanvars cleanvars,
                                    Region region, Language language, UserAgent userAgent) {

        List<Object[]> result = new ArrayList<>();

//        for (Poi2Entry poi2Entry : getPoiItems(region, language, userAgent)) {
//            result.add(new Object[]{poi2Entry.getId(), poi2Entry});
//        }

        return result;
    }
//
//    public static List<Poi2Entry> getPoiItems(Region region, Language language, UserAgent userAgent) {
//        return allExports(POI_2);
//    }
//
//    public static List<Poi2Entry> getPoiPromoItems(Region region, Language language, UserAgent userAgent) {
//        return exports(POI_2, having(on(Poi2Entry.class).getPromo(), not(equalTo(0))));
//    }

}
