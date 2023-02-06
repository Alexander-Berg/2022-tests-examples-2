package ru.yandex.autotests.turkey.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import java.util.Arrays;
import java.util.List;
import java.util.Random;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_FIVE_LETTERS;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_NO_LETTERS;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_ONE_LETTER;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_TWO_LETTERS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.DRAG_ME;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.LOGOUT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.OTHER_SETTINGS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.PASSPORT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.REGION;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.SETHOME;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.SETHOME_DESCR;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.LOGIN;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
/**
 * User: alex89
 * Date: 11.10.12
 */
public class HeaderData {
    private static final Properties CONFIG = new Properties();

    public static final String PASSPORT_HREF = "https://passport.yandex.com.tr/";
    public static final String PASSPORT_MODE_HREF = PASSPORT_HREF + "passport?mode=";

    private static final Matcher<String> PASSPORT_HREF_MATCHER =
            equalTo("https://passport.yandex.com.tr/profile");

    public static final String MAIL_HREF = "https://mail.yandex.com.tr/";
    public static final Matcher<String> MAIL_INBOX_URL_MATCHER =
            matches("\\Q" + MAIL_HREF + "\\E\\?uid=\\d+&login=[^&]+#inbox");

    private static final Matcher<String> MAIL_HREF_MATCHER =
            equalTo(MAIL_HREF);

    public static final Matcher<String> SET_HOME_TEXT = equalTo(getTranslation(SETHOME, CONFIG.getLang()));
    public static final Matcher<String> SET_HOME_HREF = equalTo("https://download.cdn.yandex.net/element/firefox/homeset/tr/homeset.xpi");
    public static final String CLID = "/?clid=" + new Random().nextInt(10000);
    public static final Matcher<String> SET_HOME_POPUP_TEXT =
            equalTo(getTranslation(SETHOME_DESCR, CONFIG.getLang()).replace("\n", ""));
    public static final Matcher<String> SET_HOME_POPUP_ICON_TEXT = equalTo(getTranslation(DRAG_ME, CONFIG.getLang()));
    public static final Matcher<String> SET_HOME_POPUP_LINK_HREF_PATTERN =
            matches(CONFIG.getBaseURL() + "\\/\\?clid=([0-9]+)");


    public static final LinkInfo PASSPORT_LINK = new LinkInfo(
            equalTo(getTranslation(PASSPORT, CONFIG.getLang())),
            PASSPORT_HREF_MATCHER,
            hasAttribute(HREF, equalTo("https://passport.yandex.com.tr/passport?mode=passport"))
    );

    public static final LinkInfo MAIL_LINK = new LinkInfo(
            equalTo(getTranslation(LOGIN, CONFIG.getLang())),
            MAIL_HREF_MATCHER
    );

    public static final LinkInfo SETTINGS_LINK = new LinkInfo(
            equalTo(getTranslation("home", "spok_yes", "head.otherSettings", CONFIG.getLang())),
            startsWith(CONFIG.getProtocol() + "://yandex.com.tr/tune/search/?retpath=" +
                    UrlManager.encodeRequest(CONFIG.getBaseURL()) + "%2F"),
            hasAttribute(HREF, startsWith(CONFIG.getProtocol() + "://yandex.com.tr/tune/search/?retpath=" +
                            UrlManager.encodeRequest(CONFIG.getBaseURL()) + "%2F"
            ))
    );

    public static final LinkInfo REGION_LINK = new LinkInfo(
            equalTo(getTranslation(REGION, CONFIG.getLang())),
            startsWith(CONFIG.getProtocol() + "://yandex.com.tr/tune/geo/?retpath=" +
                    UrlManager.encodeRequest(CONFIG.getBaseURL()) + "%2F"),
            hasAttribute(HREF, startsWith(CONFIG.getProtocol() + "://yandex.com.tr/tune/geo/?retpath=" +
                            UrlManager.encodeRequest(CONFIG.getBaseURL()) + "%2F"
            ))
    );

    public static final LinkInfo LOGOUT_LINK = new LinkInfo(
            equalTo(getTranslation(LOGOUT, CONFIG.getLang())),
            startsWith(CONFIG.getBaseURL()),
            hasAttribute(HREF, startsWith(PASSPORT_MODE_HREF + "logout"))
    );

    public static final LinkInfo MAIL_EMPTY_LINK = new LinkInfo(
            equalTo("0"),
            MAIL_INBOX_URL_MATCHER,
            hasAttribute(HREF, MAIL_HREF_MATCHER)
    );

    public static final LinkInfo ONE_LETTERS_LINK = new LinkInfo(
            equalTo("1"),
            MAIL_INBOX_URL_MATCHER,
            hasAttribute(HREF, MAIL_HREF_MATCHER)
    );

    public static final LinkInfo TWO_LETTERS_LINK = new LinkInfo(
            equalTo("2"),
            MAIL_INBOX_URL_MATCHER,
            hasAttribute(HREF, MAIL_HREF_MATCHER)
    );

    public static final LinkInfo FIVE_LETTERS_LINK = new LinkInfo(
            equalTo("5"),
            MAIL_INBOX_URL_MATCHER,
            hasAttribute(HREF, MAIL_HREF_MATCHER)
    );

    public static final List<Object[]> CNT_LETTERS_LINK = Arrays.asList(
            new Object[]{TURKEY_NO_LETTERS, MAIL_EMPTY_LINK},
            new Object[]{TURKEY_ONE_LETTER, ONE_LETTERS_LINK},
            new Object[]{TURKEY_TWO_LETTERS, TWO_LETTERS_LINK},
            new Object[]{TURKEY_FIVE_LETTERS, FIVE_LETTERS_LINK}
    );
}
