package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordamobile.Properties;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Rates.TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22.05.13
 */
public class RatesData {
    public static final Properties CONFIG = new Properties();

    public static final Matcher<String> RATES_TITLE = equalTo(getTranslation(TITLE, CONFIG.getLang()));
}
