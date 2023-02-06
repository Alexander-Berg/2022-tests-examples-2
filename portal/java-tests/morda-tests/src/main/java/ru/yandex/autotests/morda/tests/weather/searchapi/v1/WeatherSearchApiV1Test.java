package ru.yandex.autotests.morda.tests.weather.searchapi.v1;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.tests.MordaTestTags;
import ru.yandex.qatools.allure.annotations.Features;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
@Aqua.Test(title = MordaTestTags.WEATHER)
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V1, MordaTestTags.WEATHER})
@RunWith(Parameterized.class)
public class WeatherSearchApiV1Test {//extends BaseSearchApiTest {
//
//    public WeatherSearchApiV1Test(GeobaseRegion region, MordaLanguage language) {
//        super(V1, WEATHER, region, language);
//    }
//
//    @Parameterized.Parameters(name = "{0}, {1}")
//    public static Collection<Object[]> data() {
//        return new WeatherSearchApiCasesProvider(CONFIG.pages().getEnvironment())
//                .getTestCases(CONFIG.getTestMode());
//    }
}
