package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.utils.morda.region.Region;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.AFTERNOON;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.EVENING;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.MORNING;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.NIGHT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.WEATHER_TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.RegionManager.getHour;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class WeatherData {
    private static final Properties CONFIG = new Properties();

    public static final Matcher<String> TITLE = equalTo(getTranslation(WEATHER_TITLE, CONFIG.getLang()));
    public static final String TEMPERATURE_PATTERN = "(0|([+-][1-9]\\d?))";

    public static final LinkInfo WEATHER_LINK = new LinkInfo(
            not(""),
            startsWith("https://pogoda.yandex.ru/")
    );

    public static final Matcher<String> FORECAST;

    static {
        DayTime dayTime = DayTime.getDayTime(CONFIG.getBaseDomain().getCapital());
        FORECAST = matches(TEMPERATURE_PATTERN + "\n" + getTranslation(dayTime.getText(), CONFIG.getLang()) +
                " " + TEMPERATURE_PATTERN);
    }

    private static enum DayTime {
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

        public TextID getText() {
            return text;
        }
    }
}
