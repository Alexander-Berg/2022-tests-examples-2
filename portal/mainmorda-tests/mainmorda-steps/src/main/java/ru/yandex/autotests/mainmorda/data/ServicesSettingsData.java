package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.SERVICE_NO_SIGNS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.SERVICE_SERVICE_TEXT;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff
 * Date: 28.01.13
 */
public class ServicesSettingsData {
    private static final Properties CONFIG = new Properties();

    public static final Matcher<String> ADD_ALL_TEXT = equalTo("»»");
    public static final Matcher<String> ADD_TEXT = equalTo("»");
    public static final Matcher<String> REMOVE_ALL_TEXT = equalTo("««");
    public static final Matcher<String> REMOVE_TEXT = equalTo("«");

    public static final Matcher<String> SERVICES_TITLE_TEXT =
            equalTo(getTranslation(SERVICE_SERVICE_TEXT, CONFIG.getLang()));
    public static final Matcher<String> NO_SIGNS_TEXT = equalTo(getTranslation(SERVICE_NO_SIGNS, CONFIG.getLang()));

    public static final int SERVICES_WITH_COMMENTS_MAX = 4;
    public static final int SERVICES_WITH_COMMENTS_MAX_DOMAIN = 5;
}
