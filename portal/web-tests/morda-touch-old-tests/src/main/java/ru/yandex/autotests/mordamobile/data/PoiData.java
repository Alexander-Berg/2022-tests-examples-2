package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordamobile.Properties;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.POI_TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class PoiData {
    public static final Properties CONFIG = new Properties();

    public static final Matcher<String> TITLE = equalTo(getTranslation(POI_TITLE, CONFIG.getLang()));
}
