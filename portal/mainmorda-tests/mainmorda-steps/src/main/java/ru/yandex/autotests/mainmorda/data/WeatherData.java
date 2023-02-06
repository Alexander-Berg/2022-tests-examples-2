package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Description;
import org.hamcrest.Factory;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.data.WeatherPhenomena;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.region.RegionManager;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.HashMap;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mainmorda.data.WeatherData.WeatherPhenomenaMatcher.isValidPhenomenon;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.AFTERNOON;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.EVENING;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.MORNING;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.NIGHT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Weather.WEATHER_TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.RegionManager.getHour;

/**
 * User: leonsabr
 * Date: 19.03.12
 */
public class WeatherData {
    private static final Properties CONFIG = new Properties();

    private static final HashMap<Domain, String> WEATHER_CAPITALS_URLS = new HashMap<Domain, String>() {{
        put(Domain.RU, "https://pogoda.yandex.ru/moscow");
        put(Domain.UA, "https://pogoda.yandex.ua/kyiv");
        put(Domain.KZ, "https://pogoda.yandex.kz/astana");
        put(Domain.BY, "https://pogoda.yandex.by/minsk");
    }};

    public static final String TEMPERATURE_FORMAT = "(0|([+−][1-9]\\d?))";
    public static final String CURRENT_TEMPERATURE_FORMAT = TEMPERATURE_FORMAT + " °C";
    public static final Matcher<String> WEATHER_ICON_SRC = matches(
            "background-image: url\\(\"http://yastatic\\.net/weather/i/icons/30x30/[a-z _-]+\\.png\"\\);");

    public static final String FORECAST_PATTERN;
    public static final String FORECAST_LINK1_TEXT;
    public static final String FORECAST_LINK2_TEXT;

    static {
        int time = RegionManager.getHour(CONFIG.getBaseDomain().getCapital());
        String pattern = "%s " + TEMPERATURE_FORMAT + ",  %s " + TEMPERATURE_FORMAT;
        FORECAST_LINK1_TEXT = getTranslation(DayTime.getDayTime(time).getText(), CONFIG.getLang());
        FORECAST_LINK2_TEXT = getTranslation(DayTime.getDayTime((time + 6) % 24).getText(), CONFIG.getLang());
        FORECAST_PATTERN = String.format(pattern, FORECAST_LINK1_TEXT, FORECAST_LINK2_TEXT);
    }

    private static final Matcher<String> WEATHER_HREF = equalTo(WEATHER_CAPITALS_URLS.get(CONFIG.getBaseDomain()));
    private static final Matcher<String> WEATHER_URL = startsWith(WEATHER_CAPITALS_URLS.get(CONFIG.getBaseDomain()));

    public static final LinkInfo WEATHER = new LinkInfo(
            equalTo(getTranslation(WEATHER_TITLE, CONFIG.getLang())),
            WEATHER_URL,
            hasAttribute(HtmlAttribute.HREF, WEATHER_HREF));

    public static final LinkInfo WEATHER_ICON = new LinkInfo(
            equalTo(""),
            WEATHER_URL,
            hasAttribute(HtmlAttribute.TITLE, isValidPhenomenon()),
            hasAttribute(HtmlAttribute.HREF, WEATHER_URL)
    );

    public static final LinkInfo WEATHER_TEMP = new LinkInfo(
            matches(WeatherData.CURRENT_TEMPERATURE_FORMAT),
            WEATHER_URL,
            hasAttribute(HtmlAttribute.HREF, WEATHER_HREF));

    public static final LinkInfo FORECAST_LINK1 = new LinkInfo(
            startsWith(FORECAST_LINK1_TEXT),
            WEATHER_URL,
            hasAttribute(HtmlAttribute.HREF, WEATHER_HREF));

    public static final LinkInfo FORECAST_LINK2 = new LinkInfo(
            startsWith(FORECAST_LINK2_TEXT),
            WEATHER_URL,
            hasAttribute(HtmlAttribute.HREF, WEATHER_HREF));

    public static class WeatherPhenomenaMatcher extends TypeSafeMatcher<String> {
        @Override
        public void describeTo(Description description) {
            //To change body of implemented methods use File | Settings | File Templates.
        }

        @Override
        protected boolean matchesSafely(String s) {
            return WeatherPhenomena.isValidPhenomenon(CONFIG.getLang(), s);
        }

        @Factory
        public static Matcher<String> isValidPhenomenon() {
            return new WeatherPhenomenaMatcher();
        }


    }

    protected static enum DayTime {
        MORNING_TIME(0, MORNING),
        AFTERNOON_TIME(1, AFTERNOON),
        EVENING_TIME(2, EVENING),
        NIGHT_TIME(3, NIGHT);

        private DayTime(int value, TextID text) {
            this.value = value;
            this.text = text;
        }

        private int value;
        private TextID text;

        public static DayTime getDayTime(Region region) {
            int value = getHour(region) / 6;
            for (DayTime d : values()) {
                if (d.value == value) {
                    return d;
                }
            }
            return null;
        }

        public static DayTime getDayTime(int hour) {
            int value = hour / 6;
            for (DayTime d : values()) {
                if (d.value == value) {
                    return d;
                }
            }
            return null;
        }

        public TextID getText() {
            return text;
        }
    }
}
