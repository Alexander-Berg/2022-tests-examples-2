package ru.yandex.autotests.morda.tests.services.searchapi.v2;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.search.SearchApiDp;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.api.search.v2.SearchApiV2Request;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.data.services.searchapi.ServicesSearchApiV2Data;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.rules.allure.AllureLoggingRule;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.autotests.morda.tests.MordaTestsProperties;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.Tag;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.SERVICES;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
@Aqua.Test(title = "Данные SearchApi-v2 Services")
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V2, MordaTestTags.SERVICES})
@RunWith(Parameterized.class)
@Tag("sandbox")
public class ServicesV2ContentTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();
    private SearchApiRequestData requestData;
    private ServicesSearchApiV2Data servicesData;

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();

    public ServicesV2ContentTest(SearchApiRequestData requestData) {
        this.requestData = requestData;
        this.servicesData = new ServicesSearchApiV2Data(requestData);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<SearchApiRequestData> data() {
        List<SearchApiRequestData> data = new ArrayList<>();
        for (GeobaseRegion region : asList(MOSCOW, KYIV, MINSK, ASTANA)) {
            for (MordaLanguage language : asList(RU, UK, BE, KK)) {
                data.add(new SearchApiRequestData().setGeo(region).setLanguage(language).setBlock(SERVICES));
            }
            for (SearchApiDp dp : SearchApiDp.values()) {
                data.add(new SearchApiRequestData().setGeo(region).setLanguage(RU).setDp(dp).setBlock(SERVICES));
            }
        }

        return data;//.subList(0, 1);
    }

    @Test
    public void content() {
        SearchApiV2Response response = new SearchApiV2Request(CONFIG.pages().getEnvironment(), requestData).read();

        servicesData.check(response);
    }
}
