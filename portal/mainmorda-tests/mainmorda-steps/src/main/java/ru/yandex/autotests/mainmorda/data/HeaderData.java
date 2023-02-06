package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.utils.morda.url.UrlManager;
import ru.yandex.autotests.utils.morda.users.User;

import java.util.HashMap;
import java.util.Map;

import static ch.lambdaj.function.matcher.OrMatcher.or;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.startsWith;
import static org.hamcrest.text.IsEqualIgnoringCase.equalToIgnoringCase;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.OTHER_LANG;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.DRAG_ME;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.DROP_THEME;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.LANG;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.OTHER_SETTINGS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.REGION;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.SETHOME_DESCR;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.SETYANDEX;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.THEME;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.WIDGET_CATALOG;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Header.PASSPORT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.LOGIN;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Metrika.METRIKA_TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Tabs.DISK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Head.CHANGE_PASSWORD;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.KAZAN;

/**
 * User: eoff
 * Date: 10.07.12
 */
public class HeaderData {
    private static final Properties CONFIG = new Properties();

    private static final Map<Language, String> LANGUAGE_SWITCHER_CODES = new HashMap<Language, String>() {{
        put(Language.RU, "Rus");
        put(Language.TT, "Tat");
        put(Language.UK, "Ukr");
        put(Language.BE, "Bel");
        put(Language.KK, "Kaz");
    }};

    public static final String DEFAULT_LANG_CODE;
    public static final String NATIONAL_LANG_CODE;
    public static final String THIRD_LANG_CODE;
    public static final Language DEFAULT_LANG;
    public static final Language NATIONAL_LANG;
    public static final Language THIRD_LANG;

    static {
        if (CONFIG.getBaseDomain().equals(Domain.UA)) {
            DEFAULT_LANG = Language.UK;
            NATIONAL_LANG = Language.RU;
            THIRD_LANG = Language.KK;
        } else {
            DEFAULT_LANG = Language.RU;
            NATIONAL_LANG = CONFIG.getBaseDomain().getNationalLanguage();
            THIRD_LANG = Language.UK;
        }
        DEFAULT_LANG_CODE = LANGUAGE_SWITCHER_CODES.get(DEFAULT_LANG);
        NATIONAL_LANG_CODE = LANGUAGE_SWITCHER_CODES.get(NATIONAL_LANG);
        THIRD_LANG_CODE = LANGUAGE_SWITCHER_CODES.get(THIRD_LANG);
    }


    private static final String MAIL_HREF_PATTERN = "https://mail.yandex%s/";
    private static final String MAIL_HREF_HTTPS_PATTERN = "https://mail.yandex%s/neo2/#inbox";
    private static final String MAIL_HREF_HTTPS_PATTERN_SHORT = "https://mail.yandex%s/neo2/#inbox";
    private static final Matcher<String> MAIL_HREF = equalTo(String.format(MAIL_HREF_PATTERN, CONFIG.getBaseDomain()));
    private static final Matcher<String> MAIL_URL =
            or(equalTo(String.format(MAIL_HREF_HTTPS_PATTERN, CONFIG.getBaseDomain())),
                    equalTo(String.format(MAIL_HREF_HTTPS_PATTERN_SHORT, CONFIG.getBaseDomain())));

    private static final Matcher<String> DISK_HREF = equalTo("http://disk.yandex.ru/");
    private static final Matcher<String> DISK_URL = equalTo("https://disk.yandex.ru/client/disk");

    private static final String METRIKA_HREF_PATTERN = "http://metrika.yandex%s/";
    private static final Matcher<String> METRIKA_HREF =
            equalTo(String.format(METRIKA_HREF_PATTERN, CONFIG.getBaseDomain()));
    private static final Matcher<String> METRIKA_URL =
            startsWith(String.format(METRIKA_HREF_PATTERN, CONFIG.getBaseDomain()));

    private static final Matcher<String> PASSPORT_HREF = equalTo("https://passport.yandex.ru/passport?mode=passport");

    private static final Matcher<String> CHANGE_PASSWORD_URL =
            startsWith("https://passport.yandex.ru/profile/password?retpath=");
    private static final Matcher<String> CHANGE_PASSWORD_HREF =
            startsWith("https://passport.yandex.ru/passport?mode=changepass&retpath=");

    private static final String TUNE_HREF = CONFIG.getProtocol() + "://tune.yandex.ru";// + CONFIG.getBaseDomain();

    private static final Matcher<String> TUNE_HREF_MATCHER = startsWith(TUNE_HREF);
    private static final Matcher<String> TUNE_HREF_DOMAIN_MATCHER =
            startsWith(CONFIG.getProtocol() + "://tune.yandex" + CONFIG.getBaseDomain());

    private static final Matcher<String> SETUP_YANDEX_HREF = equalTo(CONFIG.getBaseURL() + "/?edit=1");

    private static final Matcher<String> ADD_WIDGET_HREF =
            startsWith(CONFIG.getProtocol() + "://widgets.yandex" + CONFIG.getBaseDomain() + "/");

    private static final Matcher<String> SET_THEME_HREF = equalTo(CONFIG.getBaseURL() + "/themes");

    private static final Matcher<String> CHANGE_CITY_HREF = equalTo(TUNE_HREF + "/region/?retpath=" +
            UrlManager.encodeRetpath(CONFIG.getBaseURL()) + "%2F%3Fdomredir%3D1");

    private static final Matcher<String> LANG_SWITCHER_HREF = startsWith(TUNE_HREF + "/lang/?retpath=" +
            UrlManager.encodeRetpath(CONFIG.getBaseURL()) + "%2F");

    private static final Matcher<String> LANG_SWITCHER_TITLE_DEFAULT = equalTo(getTranslation(LANG, DEFAULT_LANG));
    private static final Matcher<String> LANG_SWITCHER_TITLE_THIRD = equalTo(getTranslation(LANG, THIRD_LANG));

    private static final Matcher<String> CHANGE_CITY_THEMES_HREF = equalTo(TUNE_HREF + "/region/?retpath=" +
            UrlManager.encodeRetpath(CONFIG.getBaseURL()) + "%2Fthemes%3Fdomredir%3D1");

    private static final Matcher<String> OTHER_SETTINGS_HREF = equalTo(TUNE_HREF + "/?retpath=" +
            UrlManager.encodeRetpath(CONFIG.getBaseURL()) + "%2F%3Fdomredir%3D1");

    private static final Matcher<String> OTHER_SETTINGS_THEME_HREF = equalTo(TUNE_HREF + "/?retpath=" +
            UrlManager.encodeRetpath(CONFIG.getBaseURL()) + "%2Fthemes%3Fdomredir%3D1");


    public static final Region LANG_CITY;

    static {
        if (CONFIG.getBaseDomain().equals(Domain.RU)) {
            LANG_CITY = KAZAN;
        } else {
            LANG_CITY = CONFIG.getBaseDomain().getCapital();
        }
    }

    private static final String LANG_HREF_PATTERN = CONFIG.getBaseURL() + "/?lang=%s&sk=";
    private static final Matcher<String> DEFAULT_LANG_HREF =
            startsWith(String.format(LANG_HREF_PATTERN, DEFAULT_LANG.getExportValue()));
    private static final Matcher<String> NATIONAL_LANG_HREF;

    static {
        if (NATIONAL_LANG_CODE.equals("Tat")) {
            NATIONAL_LANG_HREF = startsWith(String.format(LANG_HREF_PATTERN, "tt"));
        } else {
            NATIONAL_LANG_HREF = startsWith(String.format(LANG_HREF_PATTERN, NATIONAL_LANG.getExportValue()));
        }
    }

    private static final String THIRD_LANG_HREF = String.format(LANG_HREF_PATTERN, THIRD_LANG_CODE);

    public static final Matcher<String> MAIL_LONG_LOGIN_TEXT = equalTo("header-test01234567…");
    public static final String SET_THEME_URL_PATTERN = CONFIG.getBaseURL() + "/themes/weather/set?sk=";
    public static final String DROP_THEME_HREF_PATTERN = CONFIG.getBaseURL() + "/themes/default/set?sk=";

    private static final Matcher<String> MAIL_NAME_HREF = equalTo("https://i.yandex.ru/");

    public static final String BETA_URL = CONFIG.getBaseURL().replace("www", "beta");
    public static final String CLID = "/?clid=2122758";
    public static final Matcher<String> SET_HOME_TEXT =
            equalTo(getTranslation("home", "head", "sethomeSplitted", CONFIG.getLang()).replaceAll("#", ""));
    public static final Matcher<String> SET_HOME_HREF =
            equalTo("https://download.cdn.yandex.net/element/firefox/homeset/ru/homeset.xpi");
    public static final Matcher<String> SET_HOME_POPUP_TEXT =
            equalTo(getTranslation(SETHOME_DESCR, CONFIG.getLang()).replace("\n", ""));
    public static final Matcher<String> SET_HOME_POPUP_ICON_TEXT = equalTo(getTranslation(DRAG_ME, CONFIG.getLang()));
    public static final Matcher<String> SET_HOME_POPUP_LINK_HREF_PATTERN =
            matches(CONFIG.getBaseURL() + "\\/\\?clid=([0-9]+)");


    public static LinkInfo getNameLink(User user) {
        return new LinkInfo(
                equalTo(user.getLogin()),
                startsWith(CONFIG.getBaseURL()),
                hasAttribute(HtmlAttribute.HREF, MAIL_NAME_HREF)
        );
    }

    public static LinkInfo getLongNameLink(User user) {
        return new LinkInfo(
                equalTo(user.getLogin().substring(0, 19) + "…"),
                startsWith(CONFIG.getBaseURL()),
                hasAttribute(HtmlAttribute.HREF, MAIL_NAME_HREF)
        );
    }

    public static final LinkInfo MAIL_LINK_LOGOFF = new LinkInfo(
            equalTo(getTranslation(LOGIN, CONFIG.getLang())),
            MAIL_HREF
    );

    public static final LinkInfo MAIL_LINK_LOGON = new LinkInfo(
            equalTo(getTranslation(TITLE, CONFIG.getLang())),
            MAIL_URL,
            hasAttribute(HtmlAttribute.HREF, MAIL_HREF)
    );

    public static final LinkInfo DISK_LINK = new LinkInfo(
            equalTo(getTranslation(DISK, CONFIG.getLang())),
            DISK_URL,
            hasAttribute(HtmlAttribute.HREF, DISK_HREF)
    );

    public static final LinkInfo METRIKA_LINK = new LinkInfo(
            equalTo(getTranslation(METRIKA_TITLE, CONFIG.getLang())),
            METRIKA_URL,
            hasAttribute(HtmlAttribute.HREF, METRIKA_HREF)
    );

    public static final LinkInfo PASSPORT_LINK = new LinkInfo(
            equalTo(getTranslation(PASSPORT, CONFIG.getLang())),
            PASSPORT_HREF
    );

    public static final LinkInfo CHANGE_PASS_LINK = new LinkInfo(
            equalTo(getTranslation(CHANGE_PASSWORD, CONFIG.getLang())),
            CHANGE_PASSWORD_URL,
            hasAttribute(HtmlAttribute.HREF, CHANGE_PASSWORD_HREF)
    );

    public static final LinkInfo SETUP_LINK = new LinkInfo(
            isEmptyOrNullString(),
            startsWith(CONFIG.getBaseURL()),
            hasAttribute(HtmlAttribute.HREF, TUNE_HREF_DOMAIN_MATCHER)
    );

    public static final LinkInfo SETUP_THEME_LINK = new LinkInfo(
            isEmptyOrNullString(),
            startsWith(CONFIG.getBaseURL()),
            hasAttribute(HtmlAttribute.HREF, TUNE_HREF_DOMAIN_MATCHER)
    );

    public static final LinkInfo SETUP_YANDEX_LINK = new LinkInfo(
            equalTo(getTranslation(SETYANDEX, CONFIG.getLang())),
            SETUP_YANDEX_HREF
    );

    public static final LinkInfo ADD_WIDGET_LINK = new LinkInfo(
            equalTo(getTranslation(WIDGET_CATALOG, CONFIG.getLang())),
            ADD_WIDGET_HREF
    );

    public static final LinkInfo SET_THEME_LINK = new LinkInfo(
            equalTo(getTranslation(THEME, CONFIG.getLang())),
            SET_THEME_HREF
    );

    public static final LinkInfo DROP_THEME_LINK = new LinkInfo(
            equalTo(getTranslation(DROP_THEME, CONFIG.getLang())),
            startsWith(CONFIG.getBaseURL()),
            hasAttribute(HtmlAttribute.HREF, equalTo(""))
    );

    public static final LinkInfo CHANGE_CITY_LINK = new LinkInfo(
            equalTo(getTranslation(REGION, CONFIG.getLang())),
            CHANGE_CITY_HREF
    );

    public static final LinkInfo CHANGE_CITY_THEMES_LINK = new LinkInfo(
            equalTo(getTranslation(REGION, CONFIG.getLang())),
            CHANGE_CITY_THEMES_HREF
    );

    public static final LinkInfo OTHER_SETTINGS_LINK = new LinkInfo(
            equalTo(getTranslation(OTHER_SETTINGS, CONFIG.getLang())),
            OTHER_SETTINGS_HREF
    );

    public static final LinkInfo OTHER_SETTINGS_THEME_LINK = new LinkInfo(
            equalTo(getTranslation(OTHER_SETTINGS, CONFIG.getLang())),
            OTHER_SETTINGS_THEME_HREF
    );

    public static final LinkInfo DEFAULT_LANG_SWITCHER_LINK = new LinkInfo(
            equalTo(DEFAULT_LANG_CODE),
            startsWith(CONFIG.getBaseURL()),
            hasAttribute(HtmlAttribute.HREF, LANG_SWITCHER_HREF),
            hasAttribute(HtmlAttribute.TITLE, LANG_SWITCHER_TITLE_DEFAULT)
    );

    public static final LinkInfo THIRD_LANG_SWITCHER_LINK = new LinkInfo(
            equalTo(THIRD_LANG_CODE),
            startsWith(CONFIG.getBaseURL()),
            hasAttribute(HtmlAttribute.HREF, LANG_SWITCHER_HREF),
            hasAttribute(HtmlAttribute.TITLE, LANG_SWITCHER_TITLE_THIRD)
    );

    public static final LinkInfo DEFAULT_LANG_LINK = new LinkInfo(
            equalToIgnoringCase(DEFAULT_LANG_CODE),
            startsWith(CONFIG.getBaseURL()),
            hasAttribute(HtmlAttribute.HREF, DEFAULT_LANG_HREF)
    );

    public static final LinkInfo NATIONAL_LANG_LINK = new LinkInfo(
            equalToIgnoringCase(NATIONAL_LANG_CODE),
            startsWith(CONFIG.getBaseURL()),
            hasAttribute(HtmlAttribute.HREF, NATIONAL_LANG_HREF)
    );

    public static final LinkInfo MORE_LANG_LINK = new LinkInfo(
            equalTo(getTranslation(OTHER_LANG, DEFAULT_LANG)),
            LANG_SWITCHER_HREF
    );

    public static final LinkInfo THREE_MORE_LANG_LINK = new LinkInfo(
            equalTo(getTranslation(OTHER_LANG, THIRD_LANG)),
            LANG_SWITCHER_HREF
    );

    public static final int SETUP_POPUP_SIZE = 5;
    public static final int SETUP_POPUP_CHOOSE_THEME_SIZE = 2;
    public static final int SETUP_POPUP_THEME_SIZE = 6;
}

