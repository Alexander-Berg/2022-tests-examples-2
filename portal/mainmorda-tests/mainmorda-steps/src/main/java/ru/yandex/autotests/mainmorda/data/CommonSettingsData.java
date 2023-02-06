package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Preferences.WIDGET_SETTINGS_AUTO_RELOAD;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Preferences.WIDGET_SETTINGS_CLOSE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Preferences.WIDGET_SETTINGS_OK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Preferences.WIDGET_SETTINGS_RESET;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Preferences.WIDGET_SETTINGS_TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff
 * Date: 14.12.12
 */
public class CommonSettingsData {
    private static final Properties CONFIG = new Properties();

    public static final Matcher<String> CLOSE_TEXT = equalTo(getTranslation(WIDGET_SETTINGS_CLOSE, CONFIG.getLang()));
    public static final Matcher<String> OK_TEXT = equalTo(getTranslation(WIDGET_SETTINGS_OK, CONFIG.getLang()));
    public static final Matcher<String> RESET_TEXT = equalTo(getTranslation(WIDGET_SETTINGS_RESET, CONFIG.getLang()));
    public static final Matcher<String> AUTO_RELOAD =
            equalTo(getTranslation(WIDGET_SETTINGS_AUTO_RELOAD, CONFIG.getLang()));
    public static final Matcher<String> SETTINGS_TITLE =
            equalTo(getTranslation(WIDGET_SETTINGS_TITLE, CONFIG.getLang()));
}
