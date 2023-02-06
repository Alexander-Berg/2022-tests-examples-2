package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import java.util.Arrays;
import java.util.List;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.SEARCH;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.TAB_IMAGES;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.TAB_MAPS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.TAB_MARKET;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.TAB_VIDEO;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encode;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class SearchData {
    private static final Properties CONFIG = new Properties();

    public static final Matcher<String> SEARCH_BUTTON_TEXT = equalTo(getTranslation(SEARCH, CONFIG.getLang()));

    public static final String TEXT = "sample здесь";
    public static final String SEARCH_URL_PATTERN = CONFIG.getProtocol() + "://yandex%s/search/touch/?text=%s&lr=";
    public static final String SEARCH_URL =
            String.format(SEARCH_URL_PATTERN, CONFIG.getBaseDomain(), encode(TEXT));

    public static final List<String> REQUEST_DATA = Arrays.asList("cat dog", "yandex", "download mp3");

    private static final String TUNE_URL_PATTERN = "http://m.tune.yandex.ru/?retpath=%s";

    public static final String TUNE_URL = String.format(TUNE_URL_PATTERN, encode(CONFIG.getBaseURL() + "/"));

    public static final String REQUEST = "javascript здесь";
    private static final String ENCODED_REQUEST = UrlManager.encodeRequest(REQUEST);

    public static final TabInfo MAPS_TAB = new TabInfo(
            equalTo(getTranslation(TAB_MAPS, CONFIG.getLang())),
            startsWith("intent://maps.yandex.ru/"),
            allOf(startsWith("intent://maps.yandex.ru/?"), containsString("text=" + ENCODED_REQUEST)),
            hasAttribute(HREF, startsWith("https://maps.yandex.ru/"))
    );

    public static final TabInfo VIDEO_TAB = new TabInfo(
            equalTo(getTranslation(TAB_VIDEO, CONFIG.getLang())),
            startsWith("http://yandex.ru/video/touch"),
            allOf(startsWith("http://yandex.ru/video/touch/search"), containsString("text=" + ENCODED_REQUEST)),
            hasAttribute(HREF, startsWith(CONFIG.getProtocol() + "://yandex.ru/video/touch"))
    );

    public static final TabInfo MARKET_TAB = new TabInfo(
            equalTo(getTranslation(TAB_MARKET, CONFIG.getLang())),
            startsWith("https://m.market.yandex.ru/"),
            allOf(startsWith("https://m.market.yandex.ru/search?"), containsString("text=" + ENCODED_REQUEST))
    );

    public static final TabInfo IMAGES_TAB = new TabInfo(
            equalTo(getTranslation(TAB_IMAGES, CONFIG.getLang())),
            startsWith("https://yandex.ru/images/touch"),
            allOf(startsWith("https://yandex.ru/images/touch/search?"), containsString("text=" + ENCODED_REQUEST)),
            hasAttribute(HREF, startsWith(CONFIG.getProtocol() + "://yandex.ru/images/"))
    );

    public static final List<TabInfo> ALL_TABS = Arrays.asList(MAPS_TAB, VIDEO_TAB, MARKET_TAB, IMAGES_TAB);

    public static class TabInfo extends LinkInfo {
        public Matcher<String> request;

        public TabInfo(Matcher<String> text, Matcher<String> url) {
            super(text, url);
        }

        public TabInfo(Matcher<String> text, Matcher<String> url, Matcher<String> request) {
            super(text, url);
            this.request = request;
        }

        public TabInfo(Matcher<String> text, Matcher<String> url, Matcher<String> request,
                       HtmlAttributeMatcher... htmlAttributeMatchers) {
            super(text, url, htmlAttributeMatchers);
            this.request = request;
        }
    }
}
