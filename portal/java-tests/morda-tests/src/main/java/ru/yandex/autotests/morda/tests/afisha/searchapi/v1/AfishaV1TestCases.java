package ru.yandex.autotests.morda.tests.afisha.searchapi.v1;

import ru.yandex.autotests.morda.api.search.SearchApiClient;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.api.search.v1.SearchApiV1Request;
import ru.yandex.geobase.regions.GeobaseRegion;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.AFISHA;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;
import static ru.yandex.geobase.regions.Belarus.GOMEL;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Kazakhstan.ALMATY;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.DUBNA;
import static ru.yandex.geobase.regions.Russia.KAZAN;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Russia.NIZHNY_NOVGOROD;
import static ru.yandex.geobase.regions.Russia.NOVOSIBIRSK;
import static ru.yandex.geobase.regions.Russia.OMSK;
import static ru.yandex.geobase.regions.Russia.SAINT_PETERSBURG;
import static ru.yandex.geobase.regions.Russia.SAMARA;
import static ru.yandex.geobase.regions.Russia.VLADIVOSTOK;
import static ru.yandex.geobase.regions.Russia.VORONEZH;
import static ru.yandex.geobase.regions.Russia.YEKATERINBURG;
import static ru.yandex.geobase.regions.Ukraine.KHARKIV;
import static ru.yandex.geobase.regions.Ukraine.KYIV;
import static ru.yandex.geobase.regions.Ukraine.LVIV;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 06/10/16
 */
public class AfishaV1TestCases {

    public static List<SearchApiV1Request> getData(String environment) {
        SearchApiClient searchApiClient = new SearchApiClient();
        List<SearchApiV1Request> data = new ArrayList<>();
        for (GeobaseRegion region : asList(
                MOSCOW, SAINT_PETERSBURG, NOVOSIBIRSK, VLADIVOSTOK, YEKATERINBURG,
                DUBNA, VORONEZH, OMSK, KAZAN, NIZHNY_NOVGOROD, SAMARA,
                MINSK, GOMEL,
                KYIV, KHARKIV, LVIV,
                ALMATY, ASTANA
        )) {
            data.addAll(Stream.of(RU, UK, BE, KK)
                    .map(language ->
                            searchApiClient.v1(
                                    environment,
                                    new SearchApiRequestData().setBlock(AFISHA).setGeo(region).setLanguage(language)
                            ).queryParam("afisha_version", "3")
                    ).collect(Collectors.toList())
            );
        }
        return data;
    }
}
