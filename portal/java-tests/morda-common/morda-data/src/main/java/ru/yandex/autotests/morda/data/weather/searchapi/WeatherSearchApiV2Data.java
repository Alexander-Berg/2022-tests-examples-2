package ru.yandex.autotests.morda.data.weather.searchapi;

import org.apache.commons.lang3.StringUtils;
import org.joda.time.LocalDate;
import ru.yandex.autotests.morda.api.search.SearchApiRequestData;
import ru.yandex.autotests.morda.beans.api.search.v2.SearchApiV2Response;
import ru.yandex.autotests.morda.beans.api.search.v2.weather.WeatherApiV2;
import ru.yandex.autotests.morda.beans.api.search.v2.weather.WeatherApiV2Data;
import ru.yandex.autotests.morda.beans.api.search.v2.weather.WeatherApiV2ForecastItem;
import ru.yandex.autotests.morda.beans.api.search.v2.weather.WeatherApiV2ForecastShortItem;
import ru.yandex.autotests.morda.data.SearchApiDataUtils;
import ru.yandex.autotests.morda.data.TankerManager;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.steps.links.LinkUtils;
import ru.yandex.autotests.morda.tanker.TextID;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.qatools.allure.annotations.Step;

import javax.ws.rs.core.UriBuilder;
import java.util.HashSet;
import java.util.Set;

import static ch.lambdaj.Lambda.on;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.morda.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.matchers.NestedPropertyMatcher.hasPropertyWithValue;
import static ru.yandex.autotests.morda.matchers.YellowskinMatcher.yellowskin;
import static ru.yandex.autotests.morda.matchers.string.RegexMatcher.regex;
import static ru.yandex.autotests.morda.matchers.url.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.morda.steps.CheckSteps.checkBean;
import static ru.yandex.autotests.morda.tanker.home.ApiSearch.WEATHER_TITLE;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 17/10/16
 */
public class WeatherSearchApiV2Data {
    private SearchApiRequestData requestData;

    public WeatherSearchApiV2Data(SearchApiRequestData requestData) {
        this.requestData = requestData;
    }

    @Step("Check weather")
    public void check(SearchApiV2Response response) {
        checkExists(response);

        checkBean(response.getWeather(), hasPropertyWithValue(
                on(WeatherApiV2.class).getTitle(), equalTo(TankerManager.get(WEATHER_TITLE, requestData.getLanguage()))
        ));

        checkData(response.getWeather().getData());
    }

    @Step("Check weather data")
    public void checkData(WeatherApiV2Data weatherData) {
        checkBean(weatherData, allOfDetailed(
                hasPropertyWithValue(on(WeatherApiV2Data.class).getGeoid(), equalTo(requestData.getGeo().getRegionId()))
        ));

        checkT(weatherData);
        checkUrls(weatherData);
        checkForecast(weatherData);
        checkShortForecast(weatherData);
    }

    @Step("Check weather t2name/t3name")
    public void checkT(WeatherApiV2Data weatherData) {
        WeatherApiV2DayTime current = WeatherApiV2DayTime.getCurrent(requestData.getGeo());
        WeatherApiV2DayTime t2 = current.getNext();
        WeatherApiV2DayTime t3 = t2.getNext();

        checkBean(weatherData, allOfDetailed(
                hasPropertyWithValue(on(WeatherApiV2Data.class).getT2Name(),
                        equalTo(StringUtils.capitalize(t2.getText(requestData.getLanguage())))
                ),
                hasPropertyWithValue(on(WeatherApiV2Data.class).getT3Name(),
                        equalTo(StringUtils.capitalize(t3.getText(requestData.getLanguage())))
                )
        ));
    }

    @Step("Check urls")
    public void checkUrls(WeatherApiV2Data weatherData) {

        String detailsUrl = getDetailsUrl(weatherData);

        String noticeUrl = getTomorrowUrl(weatherData);

        checkBean(weatherData, allOfDetailed(
                hasPropertyWithValue(
                        on(WeatherApiV2Data.class).getUrl(),
                        urlMatcher(getWeatherApiV2Host())
                                .path(regex("pogoda/[^/]+"))
                ),
                hasPropertyWithValue(
                        on(WeatherApiV2Data.class).getNoticeUrl(),
                        urlMatcher(noticeUrl)
                ),
                hasPropertyWithValue(
                        on(WeatherApiV2Data.class).getUrlV5(),
                        yellowskin("#f0f0f0", "#000000", urlMatcher(detailsUrl).query("appsearch_header", "1"))
                ),
                hasPropertyWithValue(
                        on(WeatherApiV2Data.class).getNowUrl(),
                        yellowskin("#f0f0f0", "#000000", urlMatcher(detailsUrl).query("appsearch_header", "1"))
                )
        ));
    }

    @Step("Check forecast")
    public void checkForecast(WeatherApiV2Data weatherData) {
        for (WeatherApiV2ForecastItem forecastItem : weatherData.getForecast()) {
            checkForecastItem(weatherData, forecastItem);
        }
    }

    @Step("Check short forecast")
    public void checkShortForecast(WeatherApiV2Data weatherData) {
        WeatherApiV2DayTime current = WeatherApiV2DayTime.getCurrent(requestData.getGeo());
        WeatherApiV2DayTime next = current.getNext();
        for (WeatherApiV2ForecastShortItem forecastItem : weatherData.getShortForecast()) {
            checkShortForecastItem(weatherData, forecastItem, next);
            next = next.getNext();
        }
    }

    @Step("Check forecast item")
    public void checkForecastItem(WeatherApiV2Data weatherData, WeatherApiV2ForecastItem forecastItem) {
        LocalDate date = LocalDate.parse(forecastItem.getDate());
        int dayOfWeek = date.getDayOfWeek() % 7;
        int dayOfMonth = date.getDayOfMonth();

        String wdayShort = StringUtils.capitalize(TankerManager.get("home", "wday_short", "" + dayOfWeek, requestData.getLanguage()));

        checkBean(forecastItem, allOfDetailed(
                hasPropertyWithValue(on(WeatherApiV2ForecastItem.class).getUrl(), yellowskin(
                        "#f0f0f0",
                        "#000000",
                        urlMatcher(getDayUrl(weatherData, date)))
                ),
                hasPropertyWithValue(on(WeatherApiV2ForecastItem.class).getIcon(),
                        regex("https://api.yastatic.net/morda-logo/i/yandex-app/weather/black1/.*\\.png")),
                hasPropertyWithValue(on(WeatherApiV2ForecastItem.class).getIconDaynight(),
                        regex("https://api.yastatic.net/morda-logo/i/yandex-app/weather/(black1|white1)/.*\\.png")),

                hasPropertyWithValue(on(WeatherApiV2ForecastItem.class).getWeekDay(), equalTo(wdayShort + " " + dayOfMonth))
        ));
    }

    @Step("Check short forecast item")
    public void checkShortForecastItem(WeatherApiV2Data weatherData, WeatherApiV2ForecastShortItem forecastItem, WeatherApiV2DayTime dayTime) {

        checkBean(forecastItem, allOfDetailed(
                hasPropertyWithValue(on(WeatherApiV2ForecastShortItem.class).getIcon(),
                        regex("https://api.yastatic.net/morda-logo/i/yandex-app/weather/black1/.*\\.png")),
                hasPropertyWithValue(on(WeatherApiV2ForecastShortItem.class).getIconDaynight(),
                        regex("https://api.yastatic.net/morda-logo/i/yandex-app/weather/(black1|white1)/.*\\.png")),
                hasPropertyWithValue(on(WeatherApiV2ForecastShortItem.class).getUrl(), yellowskin(
                        "#f0f0f0",
                        "#000000",
                        urlMatcher(getHourlyUrl(weatherData, dayTime)))
                ),
                hasPropertyWithValue(on(WeatherApiV2ForecastShortItem.class).getText(),
                        equalTo(StringUtils.capitalize(dayTime.getText(requestData.getLanguage())))
                )
        ));
    }

    @Step("Check weather exists")
    public void checkExists(SearchApiV2Response response) {
        assertThat("response is null", response, notNullValue());
        checkBean(response, hasPropertyWithValue(on(SearchApiV2Response.class).getWeather(), notNullValue()));
    }

    public String getWeatherApiV2Host() {
        return "https://yandex" + requestData.getGeo().getKubrDomain();
    }

    public String getDetailsUrl(WeatherApiV2Data data) {
        return UriBuilder.fromUri(data.getUrl())
                .path("details")
                .build()
                .toString();
    }

    public String getTomorrowUrl(WeatherApiV2Data data) {
        return UriBuilder.fromUri(getDetailsUrl(data))
                .fragment("tomorrow")
                .build()
                .toString();
    }

    public String getHourlyUrl(WeatherApiV2Data data, WeatherApiV2DayTime dayTime) {
        return UriBuilder.fromUri(data.getUrl())
                .path("hourly")
                .queryParam("appsearch_header", "1")
                .fragment(dayTime.getHourlyAnchor())
                .build()
                .toString();
    }

    public String getDayUrl(WeatherApiV2Data data, LocalDate day) {
        return UriBuilder.fromUri(getDetailsUrl(data))
                .queryParam("appsearch_header", "1")
                .fragment("d_" + day.getDayOfMonth())
                .build()
                .toString();
    }

    @Step
    public void pingUrls(SearchApiV2Response response) {
        checkExists(response);
        WeatherApiV2Data weather = response.getWeather().getData();

        Set<String> urls = new HashSet<>();
        urls.add(weather.getUrl());
        urls.add(weather.getNoticeUrl());
        urls.add(SearchApiDataUtils.getYellowskinkUrl(weather.getUrlV5()));
        urls.add(SearchApiDataUtils.getYellowskinkUrl(weather.getNowUrl()));

        weather.getForecast().forEach(e -> urls.add(SearchApiDataUtils.getYellowskinkUrl(e.getUrl())));
        weather.getShortForecast().forEach(e -> urls.add(SearchApiDataUtils.getYellowskinkUrl(e.getUrl())));

        LinkUtils.ping(urls, requestData.getGeo(), requestData.getLanguage());
    }

    public enum WeatherApiV2DayTime {
        MORNING(ru.yandex.autotests.morda.tanker.home.Weather.MORNING, "t_morning"),
        DAY(ru.yandex.autotests.morda.tanker.home.Weather.DAY, "t_day"),
        EVENING(ru.yandex.autotests.morda.tanker.home.Weather.EVENING, "t_evening"),
        NIGHT(ru.yandex.autotests.morda.tanker.home.Weather.NIGHT, "t_night");

        private TextID textID;
        private String hourlyAnchor;

        WeatherApiV2DayTime(TextID textID, String hourlyAnchor) {
            this.textID = textID;
            this.hourlyAnchor = hourlyAnchor;
        }

        public static WeatherApiV2DayTime getCurrent(GeobaseRegion region) {
            int hour = region.getTime().getHour();
            System.out.println(region + " " + hour);
            if (hour < 6) return NIGHT;
            if (hour < 12) return MORNING;
            if (hour < 18) return DAY;
            return EVENING;
        }

        public String getText(MordaLanguage language) {
            return TankerManager.get(textID, language);
        }

        public WeatherApiV2DayTime getNext() {
            if (this == MORNING) return DAY;
            if (this == DAY) return EVENING;
            if (this == EVENING) return NIGHT;
            return MORNING;
        }

        public String getHourlyAnchor() {
            return hourlyAnchor;
        }

        public TextID getTextID() {
            return textID;
        }
    }

}
