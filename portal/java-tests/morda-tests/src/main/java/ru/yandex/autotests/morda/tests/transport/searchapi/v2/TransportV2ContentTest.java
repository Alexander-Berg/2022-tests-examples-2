package ru.yandex.autotests.morda.tests.transport.searchapi.v2;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.search.SearchApiDp;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.api.search.v2.SearchApiV2Request;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.data.transport.searchapi.TransportSearchApiV2Data;
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
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.TRANSPORT;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Russia.NIZHNY_NOVGOROD;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
@Aqua.Test(title = "Данные SearchApi-v2 Transport")
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V2, MordaTestTags.TRANSPORT})
@RunWith(Parameterized.class)
@Tag("sandbox")
public class TransportV2ContentTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();
    private SearchApiRequestData requestData;
    private TransportSearchApiV2Data transportData;

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    public TransportV2ContentTest(SearchApiRequestData requestData) {
        this.requestData = requestData;
        this.transportData = new TransportSearchApiV2Data(requestData);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<SearchApiRequestData> data() {
        List<SearchApiRequestData> data = new ArrayList<>();
        for (GeobaseRegion region : asList(
                Russia.MOSCOW, Russia.SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.VLADIVOSTOK, Russia.YEKATERINBURG,
                Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
                MINSK, Belarus.GOMEL,
                KYIV, Ukraine.KHARKIV, Ukraine.LVIV,
                Kazakhstan.ALMATY, ASTANA
        )) {
            for (MordaLanguage language : asList(RU, UK, BE, KK)) {
                data.add(new SearchApiRequestData().setGeo(region).setLanguage(language).setBlock(TRANSPORT));
            }
        }

        for (SearchApiDp dp : SearchApiDp.values()) {
            for (GeobaseRegion region : asList(MOSCOW, KYIV, MINSK, ASTANA)) {
                data.add(new SearchApiRequestData().setGeo(region).setLanguage(RU).setDp(dp).setBlock(TRANSPORT));
            }
        }
        return data;
    }

    @Test
    public void content() {
        SearchApiV2Response response = new SearchApiV2Request(CONFIG.pages().getEnvironment(), requestData).read();
        transportData.check(response);
    }
}
