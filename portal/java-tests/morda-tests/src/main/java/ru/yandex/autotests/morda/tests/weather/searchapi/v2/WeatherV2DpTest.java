package ru.yandex.autotests.morda.tests.weather.searchapi.v2;

import ar.com.hjg.pngj.ImageInfo;
import ar.com.hjg.pngj.PngReader;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.api.search.SearchApiDp;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.api.search.v2.SearchApiV2Request;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.weather.WeatherApiV2Data;
import ru.yandex.autotests.morda.beans.api.search.v2.weather.WeatherApiV2ForecastItem;
import ru.yandex.autotests.morda.beans.api.search.v2.weather.WeatherApiV2ForecastShortItem;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.restassured.requests.RestAssuredGetRequest;
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
import ru.yandex.qatools.allure.annotations.Step;

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.morda.api.search.SearchApiBlock.WEATHER;
import static ru.yandex.autotests.morda.api.search.SearchApiDp._1;
import static ru.yandex.autotests.morda.api.search.SearchApiDp._2;
import static ru.yandex.autotests.morda.api.search.SearchApiDp._3;
import static ru.yandex.autotests.morda.api.search.SearchApiDp._4;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.NIZHNY_NOVGOROD;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/08/16
 */
@Aqua.Test(title = "DP SearchApi-v2 Weather")
@Features({MordaTestTags.SEARCH_API, MordaTestTags.V2, MordaTestTags.WEATHER})
@RunWith(Parameterized.class)
@Tag("sandbox")
public class WeatherV2DpTest {
    private static final MordaTestsProperties CONFIG = new MordaTestsProperties();

    @Rule
    public AllureLoggingRule allureLoggingRule = new AllureLoggingRule();
    private String icon;

    public WeatherV2DpTest(String icon) {
        this.icon = icon;
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<String> data() {
        Set<String> icons = new HashSet<>();

        for (GeobaseRegion region : asList(
                Russia.MOSCOW, Russia.SAINT_PETERSBURG, Russia.NOVOSIBIRSK, Russia.VLADIVOSTOK, Russia.YEKATERINBURG,
                Russia.DUBNA, Russia.VORONEZH, Russia.OMSK, Russia.KAZAN, NIZHNY_NOVGOROD, Russia.SAMARA,
                Belarus.MINSK, Belarus.GOMEL,
                Ukraine.KYIV, Ukraine.KHARKIV, Ukraine.LVIV,
                Kazakhstan.ALMATY, ASTANA
        )) {
            SearchApiV2Response response =
                    new SearchApiV2Request(CONFIG.pages().getEnvironment(), new SearchApiRequestData().setGeo(region).setDp(_1).setLanguage(MordaLanguage.RU).setBlock(WEATHER)).read();
            icons.addAll(getIcons(response));
        }

        icons.addAll(icons.stream().map(e -> e.replace("white1", "black1")).collect(Collectors.toList()));
        icons.addAll(icons.stream().map(e -> e.replace("black1", "white1")).collect(Collectors.toList()));

        return icons;
    }

    private static Set<String> getIcons(SearchApiV2Response response) {
        Set<String> icons = new HashSet<>();
        if (response == null || response.getWeather() == null) {
            return icons;
        }

        WeatherApiV2Data weather = response.getWeather().getData();
        icons.add(weather.getIcon());

        for (WeatherApiV2ForecastItem forecastItem : weather.getForecast()) {
            icons.add(forecastItem.getIcon());
            icons.add(forecastItem.getIconDaynight());
        }

        for (WeatherApiV2ForecastShortItem forecastItem : weather.getShortForecast()) {
            icons.add(forecastItem.getIcon());
            icons.add(forecastItem.getIconDaynight());
        }

        return icons;
    }

    @Test
    public void dp() {
        PngReader png = new PngReader(new RestAssuredGetRequest(icon)
                .readAsResponse().asInputStream());
        ImageInfo imageInfo1 = png.imgInfo;
        png.end();

        for (SearchApiDp dp : asList(_2, _3, _4)) {
            int expW = (int) Math.round(imageInfo1.rows * dp.getMult());
            int expH = (int) Math.round(imageInfo1.cols * dp.getMult());
            checkPng(dp, icon.replace(".1.", "." + dp.getValue() + "."), expW, expH);
        }
    }

    @Step("Check size dp={0}, expW={2}, expH={3} ")
    public void checkPng(SearchApiDp dp, String url, int expW, int expH) {
        PngReader png = new PngReader(new RestAssuredGetRequest(url).readAsResponse().asInputStream());
        ImageInfo imageInfo = png.imgInfo;
        png.end();

        assertThat(imageInfo.rows, equalTo(expH));
        assertThat(imageInfo.cols, equalTo(expW));
    }

}
