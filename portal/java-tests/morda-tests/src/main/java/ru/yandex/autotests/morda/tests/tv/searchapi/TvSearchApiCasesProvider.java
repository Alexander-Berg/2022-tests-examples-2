package ru.yandex.autotests.morda.tests.tv.searchapi;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.tests.AbstractTestCasesProvider;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Kazakhstan;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;
import ru.yandex.geobase.regions.UnitedStates;

import java.util.ArrayList;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.TT;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;

public class TvSearchApiCasesProvider extends AbstractTestCasesProvider<Object[]> {

    public TvSearchApiCasesProvider(String environment) {
        super(environment);
    }

    @Override
    public List<Object[]> getBaseTestCases() {
        List<Object[]> data = new ArrayList<>();
        for (GeobaseRegion region : asList(
                Russia.MOSCOW, Russia.SAINT_PETERSBURG, Ukraine.KYIV,
                Ukraine.LVIV, Belarus.MINSK, Belarus.VITEBSK,
                Kazakhstan.ASTANA, Kazakhstan.ALMATY, UnitedStates.SAN_FRANCISCO
        )) {
            for (MordaLanguage language : asList(RU, UK, BE, KK, TT)) {
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
                new Object[]{Belarus.MINSK, BE},
                new Object[]{Kazakhstan.ASTANA, KK}
        );
    }
}