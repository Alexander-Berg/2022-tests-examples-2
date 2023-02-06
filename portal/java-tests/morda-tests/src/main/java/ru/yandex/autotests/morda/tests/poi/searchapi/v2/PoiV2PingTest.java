package ru.yandex.autotests.morda.tests.poi.searchapi.v2;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.api.search.v2.SearchApiV2Request;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.data.poi.searchapi.PoiSearchApiV2Data;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.geobase.regions.Belarus;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Russia;
import ru.yandex.geobase.regions.Ukraine;
import ru.yandex.qatools.Tag;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.POI;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;
import static ru.yandex.geobase.regions.Russia.NIZHNY_NOVGOROD;
import static ru.yandex.geobase.regions.Russia.SAINT_PETERSBURG;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
@Aqua.Test(title = "Пинги SearchApi-v2 Poi")
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V2, MordaTestTags.POI})
@RunWith(Parameterized.class)
@Tag("sandbox")
public class PoiV2PingTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();
    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();
    private SearchApiRequestData requestData;
    private PoiSearchApiV2Data poiData;

    public PoiV2PingTest(SearchApiRequestData requestData) {
        this.requestData = requestData;
        this.poiData = new PoiSearchApiV2Data(requestData);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<SearchApiRequestData> data() {
        List<SearchApiRequestData> data = new ArrayList<>();
        for (GeobaseRegion region : asList(
                Russia.MOSCOW, SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.YEKATERINBURG,
                Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
                Belarus.MINSK,
                Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV
        )) {
            for (MordaLanguage language : asList(RU, UK, BE, KK)) {
                data.add(new SearchApiRequestData().setGeo(region).setLanguage(language).setBlock(POI));
            }
        }
        return data;
    }

    @Test
    public void ping() {
        SearchApiV2Response response = new SearchApiV2Request(CONFIG.pages().getEnvironment(), requestData)
                .read();
        poiData.pingUrls(response);
    }

    @Test
    public void pingMorning() {
        SearchApiV2Response response = new SearchApiV2Request(CONFIG.pages().getEnvironment(), requestData)
                .queryParam("time","08:30")
                .read();
        poiData.pingUrls(response);
    }

    @Test
    public void pingDay() {
        SearchApiV2Response response = new SearchApiV2Request(CONFIG.pages().getEnvironment(), requestData)
                .queryParam("time","15:30")
                .read();
        poiData.pingUrls(response);
    }

    @Test
    public void pingEvening() {
        SearchApiV2Response response = new SearchApiV2Request(CONFIG.pages().getEnvironment(), requestData)
                .queryParam("time","20:30")
                .read();
        poiData.pingUrls(response);
    }

    @Test
    public void pingNight() {
        SearchApiV2Response response = new SearchApiV2Request(CONFIG.pages().getEnvironment(), requestData)
                .queryParam("time","23:40")
                .read();
        poiData.pingUrls(response);
    }

}
