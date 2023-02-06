package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.utils.morda.language.Language;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.WIDGET_REGION;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff
 * Date: 19.12.12
 */
public class WeatherSettingsData {
    private static final Properties CONFIG = new Properties();

    public static final Matcher<String> REGION_TEXT = equalTo(getTranslation(WIDGET_REGION, CONFIG.getLang()));

    public static final List<String> CITIES_INPUT = Arrays.asList(
            getTranslation("regions", "weather", "Санкт-Петербург", Language.RU),
            getTranslation("regions", "weather", "Мариуполь", Language.RU),
            getTranslation("regions", "weather", "Витебск", Language.RU),
            getTranslation("regions", "weather", "Алматы", Language.RU)
    );

    public static final Map<String, String> CITIES_TRANSLATIONS = new HashMap<String, String>();

    static {
        for (String city : CITIES_INPUT) {
            CITIES_TRANSLATIONS.put(city, getTranslation("regions", "weather", city, CONFIG.getLang()));
        }
    }
}
