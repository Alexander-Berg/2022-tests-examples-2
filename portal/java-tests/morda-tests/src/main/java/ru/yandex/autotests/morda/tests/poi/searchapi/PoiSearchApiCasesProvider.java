package ru.yandex.autotests.morda.tests.poi.searchapi;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.tests.AbstractTestCasesProvider;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;

import java.util.ArrayList;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.TT;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;
import static ru.yandex.geobase.regions.Russia.NIZHNY_NOVGOROD;
import static ru.yandex.geobase.regions.Russia.SAINT_PETERSBURG;

public class PoiSearchApiCasesProvider extends AbstractTestCasesProvider<Object[]> {

    public PoiSearchApiCasesProvider(String environment) {
        super(environment);
    }

    @Override
    public List<Object[]> getBaseTestCases() {
        List<Object[]> data = new ArrayList<>();
        for (GeobaseRegion region : asList(
                Russia.MOSCOW, SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.YEKATERINBURG,
                Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
                Belarus.MINSK,
                Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV
        )) {
            for (MordaLanguage language : asList(RU, UK, BE, KK)) {
                data.add(new Object[]{region, language});
            }
        }
        return data;
    }

    @Override
    public List<Object[]> getSmokeTestCases() {
        return asList(
                new Object[]{Russia.MOSCOW, RU},
                new Object[]{Russia.KAZAN, TT},
                new Object[]{Ukraine.KYIV, UK},
                new Object[]{Belarus.MINSK, BE}
        );
    }
}