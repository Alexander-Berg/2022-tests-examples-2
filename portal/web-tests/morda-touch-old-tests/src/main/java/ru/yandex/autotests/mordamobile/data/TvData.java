package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.utils.morda.region.Region;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.TV_TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class TvData {
    private static final Properties CONFIG = new Properties();

    private static final String TITLE_HREF_PATTERN = CONFIG.getProtocol() + "://m.tv.yandex.ru/%s";
    public static final Matcher<String> TIME_MATCHER = matches("([0-1][0-9]|2[0-3]):[0-5][0-9]");

    public static LinkInfo getTitleLink(Region region) {
        return new LinkInfo(
                equalTo(getTranslation(TV_TITLE, CONFIG.getLang())),
                startsWith(String.format(TITLE_HREF_PATTERN, region.getRegionId()))
        );
    }

    public static LinkInfo getTvEventLink(Region region) {
        return new LinkInfo(
                not(""),
                startsWith(String.format(TITLE_HREF_PATTERN, region.getRegionId()))
        );
    }

//    public static final LinkInfo TV_LINK = new LinkInfo(
//            inLanguage(CONFIG.getLang()),
//            startsWith(BLOGS_URL)
//    );
}
