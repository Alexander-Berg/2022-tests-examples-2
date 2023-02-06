package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.CANCEL_SETTINGS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.GO_HOME;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.GO_WORK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.INPUT_ADDRESS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.LOAD_ON_ROAD;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.RESET_SETTINGS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.SAVE_SETTINGS;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff
 * Date: 18.02.13
 */
public class TrafficSettingsData {
    private static final Properties CONFIG = new Properties();

    public static final Matcher<String> HOME_TEXT = equalTo(getTranslation(GO_HOME, CONFIG.getLang()));
    public static final Matcher<String> WORK_TEXT = equalTo(getTranslation(GO_WORK, CONFIG.getLang()));
    public static final Matcher<String> SAVE_BUTTON_TEXT = equalTo(getTranslation(SAVE_SETTINGS, CONFIG.getLang()));
    public static final Matcher<String> CANCEL_BUTTON_TEXT = equalTo(getTranslation(CANCEL_SETTINGS, CONFIG.getLang()));
    public static final Matcher<String> RESET_BUTTON_TEXT = equalTo(getTranslation(RESET_SETTINGS, CONFIG.getLang()));
    public static final Matcher<String> INFO_TEXT = equalTo(getTranslation(INPUT_ADDRESS, CONFIG.getLang()));
    public static final Matcher<String> TITLE_TEXT = equalTo(getTranslation(LOAD_ON_ROAD, CONFIG.getLang()));
}
