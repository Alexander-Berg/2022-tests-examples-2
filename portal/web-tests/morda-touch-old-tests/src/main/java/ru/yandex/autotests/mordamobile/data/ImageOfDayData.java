package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.IMAGES_TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class ImageOfDayData {
    private static final Properties CONFIG = new Properties();

    private static final String TITLE_HREF_PATTERN = "http://m.fotki.yandex.ru/";
    public static final Matcher<String> TIME_MATCHER = matches("([0-1][0-9]|2[0-3]):[0-5][0-9]");
    public static final Matcher<String> PHOTO_TEXT_MATCHER = equalTo(getTranslation(IMAGES_TITLE, CONFIG.getLang()));

    public static final LinkInfo TITLE_LINK = new LinkInfo(
            PHOTO_TEXT_MATCHER,
            equalTo(TITLE_HREF_PATTERN)
    );

    public static final LinkInfo IMAGE_LINK = new LinkInfo(
            equalTo(""),
            equalTo(TITLE_HREF_PATTERN)
    );


}
