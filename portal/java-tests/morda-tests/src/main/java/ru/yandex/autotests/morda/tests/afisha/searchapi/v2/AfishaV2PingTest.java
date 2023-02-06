package ru.yandex.autotests.morda.tests.afisha.searchapi.v2;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.api.search.v2.SearchApiV2Request;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.data.afisha.searchapi.AfishaSearchApiV2Data;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Kazakhstan;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;
import ru.yandex.qatools.Tag;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.AFISHA;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.NIZHNY_NOVGOROD;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
@Aqua.Test(title = "Пинги SearchApi-v2 Afisha")
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V2, MordaTestTags.AFISHA})
@RunWith(Parameterized.class)
@Tag("sandbox")
public class AfishaV2PingTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();
    private SearchApiRequestData requestData;
    private AfishaSearchApiV2Data afishaData;

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    public AfishaV2PingTest(SearchApiRequestData requestData) {
        this.requestData = requestData;
        this.afishaData = new AfishaSearchApiV2Data(requestData);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<SearchApiRequestData> data() {
        List<SearchApiRequestData> data = new ArrayList<>();
        for (GeobaseRegion region : asList(
                Russia.MOSCOW, Russia.SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.VLADIVOSTOK, Russia.YEKATERINBURG,
                Russia.DUBNA, Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
                Belarus.MINSK, Belarus.GOMEL,
                Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV,
                Kazakhstan.ALMATY, ASTANA
        )) {
            for (MordaLanguage language : asList(RU, UK, BE, KK)) {
                data.add(new SearchApiRequestData().setGeo(region).setLanguage(language).setBlock(AFISHA));
            }
        }
        return data;
    }

    @Test
    public void ping() {
        SearchApiV2Response response = new SearchApiV2Request(CONFIG.pages().getEnvironment(), requestData)
                .queryParam("afisha_version", "3")
                .read();
        afishaData.pingUrls(response);
    }
}
