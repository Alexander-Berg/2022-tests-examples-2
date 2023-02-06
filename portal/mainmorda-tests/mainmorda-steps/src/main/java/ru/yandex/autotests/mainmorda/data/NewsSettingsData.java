package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;

import java.util.HashMap;
import java.util.Map;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TOPNEWS_LANG;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TOPNEWS_LANG_AUTO;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TOPNEWS_LANG_RU;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TOPNEWS_LANG_RUUK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TOPNEWS_LANG_UK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TOPNEWS_NONUM;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TOPNEWS_NONUM_AUTO;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TOPNEWS_NONUM_HIDE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mform.TOPNEWS_NONUM_SHOW;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff
 * Date: 25.12.12
 */
public class NewsSettingsData {
    private static final Properties CONFIG = new Properties();

    public static final Matcher<String> GOOD_NEWS_TEXT = equalTo("Display \"Good news\" only");

    public static final Matcher<String> LANGUAGE_TEXT = equalTo(getTranslation(TOPNEWS_LANG, CONFIG.getLang()));
    public static final Matcher<String> ENUMERATION_TEXT = equalTo(getTranslation(TOPNEWS_NONUM, CONFIG.getLang()));

    public static final Map<String, String> ENUMERATION_MAP = new HashMap<String, String>() {{
        put("false", getTranslation(TOPNEWS_NONUM_AUTO, CONFIG.getLang()));
        put("true", getTranslation(TOPNEWS_NONUM_HIDE, CONFIG.getLang()));
        put("show", getTranslation(TOPNEWS_NONUM_SHOW, CONFIG.getLang()));
    }};

    public static final Map<String, String> LANGUAGE_MAP = new HashMap<String, String>() {{
        put("auto", getTranslation(TOPNEWS_LANG_AUTO, CONFIG.getLang()));
        put("ru", getTranslation(TOPNEWS_LANG_RU, CONFIG.getLang()));
        put("uk", getTranslation(TOPNEWS_LANG_UK, CONFIG.getLang()));
        put("ruuk", getTranslation(TOPNEWS_LANG_RUUK, CONFIG.getLang()));
    }};

    public static final int OPTION_NUMERATION_AUTO = 0;
    public static final int OPTION_NUMERATION_OFF = 1;
    public static final int OPTION_NUMERATION_ON = 2;

    public static final int OPTION_LANG_AUTO = 0;
    public static final int OPTION_LANG_RU = 1;
    public static final int OPTION_LANG_UK = 2;
    public static final int OPTION_LANG_RU_UK = 3;
}


