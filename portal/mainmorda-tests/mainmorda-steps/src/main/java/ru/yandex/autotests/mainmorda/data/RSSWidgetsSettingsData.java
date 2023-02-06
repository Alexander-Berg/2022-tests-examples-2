package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;

import java.util.Arrays;
import java.util.List;

import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Wform.RSS_GENERIC;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Wform.RSS_GENERIC_IMG;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Wform.RSS_HEIGHT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Wform.RSS_HEIGHT_AUTO;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Wform.RSS_HEIGHT_BIG;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Wform.RSS_HEIGHT_COMPACT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Wform.RSS_HEIGHT_GENERIC;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Wform.RSS_MAGAZINE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Wform.RSS_RANDOM;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Wform.RSS_NO_TEXT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Wform.RSS_TYPE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff
 * Date: 03.02.13
 */
public class RSSWidgetsSettingsData {
    private static final Properties CONFIG = new Properties();

    public static final List<WidgetsData.WidgetInfo> TEST_DATA =
            Arrays.asList(WidgetsData.LENTARU, WidgetsData.WAR_NEWS);

    private static final Matcher<String> TYPE_GENERIC = equalTo(getTranslation(RSS_GENERIC, CONFIG.getLang()));
    private static final Matcher<String> TYPE_GENERIC_IMG = equalTo(getTranslation(RSS_GENERIC_IMG, CONFIG.getLang()));
    private static final Matcher<String> TYPE_MAGAZINE = equalTo(getTranslation(RSS_MAGAZINE, CONFIG.getLang()));
    private static final Matcher<String> TYPE_RANDOM = equalTo(getTranslation(RSS_RANDOM, CONFIG.getLang()));

    private static final Matcher<String> HEIGHT_AUTO = equalTo(getTranslation(RSS_HEIGHT_AUTO, CONFIG.getLang()));
    private static final Matcher<String> HEIGHT_GENERIC = equalTo(getTranslation(RSS_HEIGHT_GENERIC, CONFIG.getLang()));
    private static final Matcher<String> HEIGHT_COMPACT = equalTo(getTranslation(RSS_HEIGHT_COMPACT, CONFIG.getLang()));
    private static final Matcher<String> HEIGHT_BIG = equalTo(getTranslation(RSS_HEIGHT_BIG, CONFIG.getLang()));


    public static final Matcher<String> TYPE_TEXT = equalTo(getTranslation(RSS_TYPE, CONFIG.getLang()));
    public static final Matcher<String> HEIGHT_TEXT = equalTo(getTranslation(RSS_HEIGHT, CONFIG.getLang()));
    public static final Matcher<String> NO_TEXT = equalTo(getTranslation(RSS_NO_TEXT, CONFIG.getLang()));

    public static final List<Matcher<String>> TYPE_LIST =
            Arrays.asList(TYPE_GENERIC, TYPE_GENERIC_IMG, TYPE_MAGAZINE, TYPE_RANDOM);
    public static final List<Matcher<String>> HEIGHT_LIST =
            Arrays.asList(HEIGHT_AUTO, HEIGHT_GENERIC, HEIGHT_COMPACT, HEIGHT_BIG);

    public static final Matcher<String> HEIGHT_GENERIC_DIV = equalTo("w-rss__body");
    public static final Matcher<String> HEIGHT_COMPACT_DIV = containsString("height_compact");
    public static final Matcher<String> HEIGHT_BIG_DIV = containsString("height_large");

    public static final Matcher<String> TYPE_TEXT_DIV = containsString("w-rss_type_text ");
    public static final Matcher<String> TYPE_TEXT_IMG_DIV = containsString("w-rss_type_text-img ");
    public static final Matcher<String> TYPE_MAGAZINE_DIV = containsString("w-rss_type_magazine ");

    public static final int SET_SIZE_GENERIC = 1;
    public static final int SET_SIZE_COMPACT = 2;
    public static final int SET_SIZE_LARGE = 3;

    public static final int SET_TYPE_TEXT = 0;
    public static final int SET_TYPE_TEXT_IMG = 1;
    public static final int SET_TYPE_MAGAZINE = 2;
}
