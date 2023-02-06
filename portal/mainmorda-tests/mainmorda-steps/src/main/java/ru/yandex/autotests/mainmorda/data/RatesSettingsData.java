package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.RATES_COLOR;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.RATES_RATE_TEXT;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff
 * Date: 25.12.12
 */
public class RatesSettingsData {
    private static final Properties CONFIG = new Properties();

    public static final Matcher<String> ADD_ALL_TEXT = equalTo("»»");
    public static final Matcher<String> ADD_TEXT = equalTo("»");
    public static final Matcher<String> REMOVE_ALL_TEXT = equalTo("««");
    public static final Matcher<String> REMOVE_TEXT = equalTo("«");

    public static final Matcher<String> RATES_TITLE = equalTo(getTranslation(RATES_RATE_TEXT, CONFIG.getLang()));
    public static final Matcher<String> RATES_HIGHLIGHT = equalTo(getTranslation(RATES_COLOR, CONFIG.getLang()));

    public static final int DEFAULT_LIST_SIZE = 5;

}
