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
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.FOOT_FEEDBACK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.FOOT_TUNE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.HEAD_ENTER;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Services.SERVICE_ALL_MOBILE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Tabs.DICTIONARIES;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Tabs.IMAGES;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Tabs.MAIL;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Tabs.MAPS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Tabs.MARKET;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Tabs.NEWS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Tabs.SERVICES;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Tabs.VIDEO;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 25.04.13
 */
public class MenuData {
    public static final Properties CONFIG = new Properties();

    public static final String REQUEST = "javascript here";

    public static final Matcher<String> TITLE_TEXT = equalTo(getTranslation(SERVICES, CONFIG.getLang()));


    private static final String IMAGES_HREF_PATTERN = CONFIG.getProtocol() + "://yandex.ru/images/";
    private static final String IMAGES_URL = "https://yandex.ru/images/touch";
    private static final String IMAGES_HREF = String.format(IMAGES_HREF_PATTERN, CONFIG.getBaseDomain());
    private static final String ENCODED_REQUEST = "text=" + UrlManager.encodeRequest(REQUEST);
    private static final Matcher<String> IMAGES_REQUEST =
            allOf(startsWith("https://yandex.ru/images/touch/search"), containsString(ENCODED_REQUEST));

    private static final String NEWS_HREF_PATTERN = "https://m.news.yandex%s/";
    private static final String NEWS_HREF = String.format(NEWS_HREF_PATTERN, CONFIG.getBaseDomain());
    private static final Matcher<String> NEWS_REQUEST = allOf(startsWith(NEWS_HREF),
            containsString(ENCODED_REQUEST));


    private static final String MAIL_HREF = "https://mail.yandex.ru/";
    private static final String MAIL_URL = "https://mail.yandex.ru/";

    private static final String MAPS_HREF = "https://maps.yandex.ru/";
    private static final String MAPS_INTENT = "intent://maps.yandex.ru/";
    private static final Matcher<String> MAPS_REQUEST = allOf(startsWith(MAPS_INTENT),
            containsString(ENCODED_REQUEST));

    private static final String MARKET_HREF = "http://m.market.yandex.ru/";
    private static final String MARKET_HTTPS_HREF = "https://m.market.yandex.ru/";
    private static final String MARKET_HOST = "m.market.yandex.ru";
    private static final Matcher<String> MARKET_REQUEST = allOf(containsString(MARKET_HOST),
            containsString(ENCODED_REQUEST));

    private static final String DICTIONARIES_HREF = CONFIG.getProtocol() + "://m.slovari.yandex.ru/";
    private static final String DICTIONARIES_URL = "https://m.slovari.yandex.ru/";
    private static final Matcher<String> DICTIONARIES_REQUEST = allOf(startsWith(DICTIONARIES_URL),
            containsString(ENCODED_REQUEST));

    private static final String VIDEO_HREF = CONFIG.getProtocol() + "://yandex.ru/video/touch";
    private static final String VIDEO_URL = "http://yandex.ru/video/touch";
    private static final Matcher<String> VIDEO_REQUEST = allOf(startsWith("http://yandex.ru/video/touch/search"),
            containsString(ENCODED_REQUEST));


    private static final String ALL_HREF = CONFIG.getBaseURL() + "/all";

    private static final String SETTINGS_HREF = CONFIG.getProtocol() + "://m.tune.yandex.ru/?retpath=" +
            UrlManager.encode(CONFIG.getBaseURL()) + "%2F%3Fdomredir%3D1";

    private static final String SETTINGS_URL = CONFIG.getProtocol() + "://m.tune.yandex.ru/?retpath=" +
            UrlManager.encode(CONFIG.getBaseURL()) + "%2F%3Fdomredir%3D1";

    private static final String FEEDBACK_HREF = "http://mobile-feedback.yandex.ru/?from=m-mainpage";

    private static final String LOGIN_URL = CONFIG.getBaseURL() + "/";
    private static final String LOGIN_HREF = CONFIG.getBaseURL() + "/";


    public static final TabInfo IMAGES_LINK = new TabInfo(
            equalTo(getTranslation(IMAGES, CONFIG.getLang())),
            startsWith(IMAGES_URL),
            IMAGES_REQUEST,
            hasAttribute(HREF, equalTo(IMAGES_HREF))
    );

    public static final TabInfo NEWS_LINK = new TabInfo(
            equalTo(getTranslation(NEWS, CONFIG.getLang())),
            equalTo(NEWS_HREF),
            NEWS_REQUEST,
            hasAttribute(HREF, equalTo(NEWS_HREF))
    );

    public static final TabInfo MAIL_LINK = new TabInfo(
            equalTo(getTranslation(MAIL, CONFIG.getLang())),
            equalTo(MAIL_URL),
            equalTo(MAIL_URL),
            hasAttribute(HREF, equalTo(MAIL_HREF))
    );

    public static final TabInfo MAPS_LINK = new TabInfo(
            equalTo(getTranslation(MAPS, CONFIG.getLang())),
            startsWith(MAPS_INTENT),
            MAPS_REQUEST,
            hasAttribute(HREF, startsWith(MAPS_HREF))
    );

    public static final TabInfo MARKET_LINK = new TabInfo(
            equalTo(getTranslation(MARKET, CONFIG.getLang())),
            containsString(MARKET_HOST),
            MARKET_REQUEST,
            hasAttribute(HREF, equalTo(MARKET_HREF))
    );

    public static final TabInfo DICTIONARIES_LINK = new TabInfo(
            equalTo(getTranslation(DICTIONARIES, CONFIG.getLang())),
            equalTo(DICTIONARIES_URL),
            DICTIONARIES_REQUEST,
            hasAttribute(HREF, equalTo(DICTIONARIES_HREF))
    );

    public static final TabInfo VIDEO_LINK = new TabInfo(
            equalTo(getTranslation(VIDEO, CONFIG.getLang())),
            startsWith(VIDEO_URL),
            VIDEO_REQUEST,
            hasAttribute(HREF, startsWith(VIDEO_HREF))
    );

    public static final TabInfo ALL_LINK = new TabInfo(
            equalTo(getTranslation(SERVICE_ALL_MOBILE, CONFIG.getLang())),
            equalTo(ALL_HREF),
            equalTo(ALL_HREF),
            hasAttribute(HREF, equalTo(ALL_HREF))
    );

    public static final TabInfo SETTINGS_LINK = new TabInfo(
            equalTo(getTranslation(FOOT_TUNE, CONFIG.getLang())),
            equalTo(SETTINGS_URL),
            equalTo(SETTINGS_URL),
            hasAttribute(HREF, equalTo(SETTINGS_HREF))
    );

    public static final TabInfo FEEDBACK_LINK = new TabInfo(
            equalTo(getTranslation(FOOT_FEEDBACK, CONFIG.getLang())),
            equalTo(FEEDBACK_HREF),
            equalTo(FEEDBACK_HREF),
            hasAttribute(HREF, equalTo(FEEDBACK_HREF))
    );

    public static final TabInfo LOGIN_LINK = new TabInfo(
            equalTo(getTranslation(HEAD_ENTER, CONFIG.getLang())),
            startsWith(LOGIN_URL),
            startsWith(LOGIN_URL),
            hasAttribute(HREF, startsWith(LOGIN_HREF))
    );

    public static final List<TabInfo> ALL_LINKS = Arrays.asList(IMAGES_LINK, NEWS_LINK, MAIL_LINK, MAPS_LINK,
            MARKET_LINK, DICTIONARIES_LINK, VIDEO_LINK, ALL_LINK, SETTINGS_LINK, FEEDBACK_LINK, LOGIN_LINK
    );


    public static class TabInfo extends LinkInfo {
        public Matcher<String> request;

        public TabInfo(Matcher<String> text, Matcher<String> url, Matcher<String> request,
                       HtmlAttributeMatcher attributes) {
            super(text, url, attributes);
            this.request = request;
        }

        public Matcher<String> getRequest() {
            return request;
        }

        @Override
        public String toString() {
            return text.toString();
        }
    }
}
