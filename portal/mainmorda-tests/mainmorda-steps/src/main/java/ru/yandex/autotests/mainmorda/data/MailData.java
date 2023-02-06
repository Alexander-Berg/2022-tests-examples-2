package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.CoreMatchers;
import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.url.UrlManager;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.SRC;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.COMPOSE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.COMPOSE_MSG;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.DO_NOT_REMEMBER;
import static ru.yandex.autotests.utils.morda.language.Dictionary.LegoIslandsUser.Auth.WRONG_KEYBOARD_LAYOUT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.LegoIslandsUser.Auth.WRONG_CHARACTERS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.LegoIslandsUser.Auth.FILL_INPUT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.LegoIslandsUser.Auth.WRONG_PASSWORD;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.FOLD;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.LOGIN;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.LOGIN_LABEL_UP;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Header.LOGOUT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.MAIL_C1;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.MAIL_C2;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.MAIL_C5;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.MAIL_EMPTY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.PASSWD_UP;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.REGISTER_MAILBOX;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.REMEMBER;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.UNFOLD;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mail.PROMO_BUTTON;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: alex89
 * Date: 06.10.12
 */
public class MailData {
    private static final Properties CONFIG = new Properties();

    public static final String RANDOM_TEXT_TR = "ğüt";
    public static final String RANDOM_TEXT_RU = "рапрпрпрпрпрпр";
    public static final String RANDOM_TEXT_EN = "yandexxxxx";
    public static final String RANDOM_TEXT_EN_2 = "rifjinoserufa";

    public static final String PASSPORT_PAGE_URL_PATTERN = "https://passport.yandex%s/";
    public static final String PASSPORT_PAGE_URL = String.format(PASSPORT_PAGE_URL_PATTERN, CONFIG.getBaseDomain());
    public static final String MAIL_PAGE_URL_HTTPS_PATTERN = "https://mail.yandex%s/";
    public static final String MAIL_PAGE_URL_HTTPS = String.format(MAIL_PAGE_URL_HTTPS_PATTERN, CONFIG.getBaseDomain());
    public static final String PASSPORT_NEW_MAIL_PAGE_URL = PASSPORT_PAGE_URL +
            "passport?mode=register&retpath=" + UrlManager.encode(MAIL_PAGE_URL_HTTPS) + "%3Forigin%3Dhome_ru_soc&origin=home_ru_soc";
    public static final Matcher<String> MAIL_PAGE_SECURE_LOGGED_URL_MATCHER =
            matches("\\Q" + MAIL_PAGE_URL_HTTPS + "\\E\\?ncrnd=\\d+&uid=\\d+&login=[^&]+#inbox");
    public static final String MAIL_COMPOSE_PAGE_LOGGED_URL = MAIL_PAGE_URL_HTTPS + "neo2/#compose";
    public static final String ICONS_SRC_WITH_HTTP = "http://yastatic.net/lego/_/La6qi18Z8LwgnZdsAr1qy1GwCwo.gif";
    public static final String ICONS_SRC_WITH_HTTPS = "https://yastatic.net/lego/_/La6qi18Z8LwgnZdsAr1qy1GwCwo.gif";
    public static final String EXIT_LINK_HREF_PATTERN = "https://passport.yandex.ru/" +
            "passport?mode=logout&target=everybody&yu=%s&retpath=%s";

    public static final String MAIL_AUTH_FAILED_PAGE_URL_PATTERN =
            "https://passport.yandex.ru/passport?mode=auth" +
                    "&retpath=https%%3A%%2F%%2Fmail.yandex%s%%2F%%3Forigin%%3Dlog_%s_nol&origin=log_%s_nol";
    public static final String MAIL_AUTH_FAILED_PAGE_URL =
            String.format(MAIL_AUTH_FAILED_PAGE_URL_PATTERN, CONFIG.getBaseDomain(),
                    CONFIG.getBaseDomain().toString().substring(1),
                    CONFIG.getBaseDomain().toString().substring(1));

    public static final String CREATE_ACCOUNT_PAGE_URL = "https://passport.yandex.ru/registration/";
    public static final String REMIND_PASSWORD_PAGE =
            "https://passport.yandex.ru/passport?mode=restore";

    public static final String CREATE_MAIL_URL = MAIL_PAGE_URL_HTTPS + "?origin=home_soc_";
    public static final LinkInfo CREATE_MAIL_LINK = new LinkInfo(
            equalTo(getTranslation(PROMO_BUTTON, CONFIG.getLang())),
            equalTo(PASSPORT_NEW_MAIL_PAGE_URL),
            hasAttribute(HREF, startsWith(CREATE_MAIL_URL))
    );

    public static LinkInfo getExitLink(String yandexUid) {
        return new LinkInfo(
                equalTo(getTranslation(LOGOUT, CONFIG.getLang())),
                startsWith(CONFIG.getBaseURL()),
                hasAttribute(HREF, CoreMatchers.startsWith(String.format(MailData.EXIT_LINK_HREF_PATTERN, yandexUid,
                        UrlManager.encodeRetpath(CONFIG.getBaseURL()))))
        );
    }

    public static final LinkInfo MAIL_TITLE_LOGGED_LINK = new LinkInfo(
            equalTo(getTranslation(TITLE, CONFIG.getLang())),
            MAIL_PAGE_SECURE_LOGGED_URL_MATCHER,
            hasAttribute(HREF, equalTo(MAIL_PAGE_URL_HTTPS))
    );

    public static final LinkInfo MAIL_TITLE_LINK = new LinkInfo(
            equalTo(getTranslation(TITLE, CONFIG.getLang())),
            startsWith(MAIL_PAGE_URL_HTTPS),
            hasAttribute(HREF, startsWith(MAIL_PAGE_URL_HTTPS))
    );

    public static final LinkInfo LETTER_LINK = new LinkInfo(
            not(isEmptyOrNullString()),
            MAIL_PAGE_SECURE_LOGGED_URL_MATCHER,
            hasAttribute(HREF, equalTo(MAIL_PAGE_URL_HTTPS))
    );

    public static final LinkInfo EXPAND_LINK = new LinkInfo(
            isEmptyOrNullString(),
            startsWith(CONFIG.getBaseURL()),
            hasAttribute(HtmlAttribute.TITLE, equalTo(getTranslation(UNFOLD, CONFIG.getLang())))
    );

    public static final LinkInfo FOLD_LINK = new LinkInfo(
            equalTo(getTranslation(FOLD, CONFIG.getLang())),
            startsWith(CONFIG.getBaseURL()),
            hasAttribute(HREF, isEmptyOrNullString())
    );

    public static final LinkInfo MAIL_COMPOSE_FOLD_LINK = new LinkInfo(
            equalTo(getTranslation(COMPOSE_MSG, CONFIG.getLang())),
            equalTo(MAIL_COMPOSE_PAGE_LOGGED_URL),
            hasAttribute(HREF, equalTo(MAIL_PAGE_URL_HTTPS + "compose"))
    );

    public static final LinkInfo MAIL_COMPOSE_FULL_LINK = new LinkInfo(
            equalTo(getTranslation(COMPOSE, CONFIG.getLang())),
            equalTo(MAIL_COMPOSE_PAGE_LOGGED_URL),
            hasAttribute(HREF, equalTo(MAIL_PAGE_URL_HTTPS + "compose"))
    );

    public static final LinkInfo MAIL_CREATE_ACCOUNT_LINK = new LinkInfo(
            equalTo(getTranslation(REGISTER_MAILBOX, CONFIG.getLang()).replace("  ", "")),
            startsWith(CREATE_ACCOUNT_PAGE_URL)
    );

    public static final LinkInfo MAIL_REMIND_PASSWORD_LINK = new LinkInfo(
            equalTo(getTranslation(REMEMBER, CONFIG.getLang()).replace("\n", " ")),
            equalTo(REMIND_PASSWORD_PAGE)
    );

    public static final Matcher<String> MAIL_ENTER_TEXT = equalTo(getTranslation(LOGIN, CONFIG.getLang()));

    public static final Matcher<HtmlElement> ICON_MATCHER =
            hasAttribute(SRC, anyOf(Matchers.equalTo(ICONS_SRC_WITH_HTTP), Matchers.equalTo(ICONS_SRC_WITH_HTTPS)));

    public static final Matcher<String> CHANGE_KEYBOARD_TEXT =
            equalTo(getTranslation(WRONG_KEYBOARD_LAYOUT, CONFIG.getLang()));
    public static final Matcher<String> WRONG_CHARS_TEXT = equalTo(getTranslation(WRONG_CHARACTERS, CONFIG.getLang()));
    public static final Matcher<String> FILL_FIELD_ERROR = equalTo(getTranslation(FILL_INPUT, CONFIG.getLang()));
    public static final Matcher<String> SAME_LOGIN_AND_PWD_ERROR =
            equalTo(getTranslation(WRONG_PASSWORD, CONFIG.getLang()));

    public static final Matcher<String> LOGIN_TEXT =
            equalTo(getTranslation(LOGIN_LABEL_UP, CONFIG.getLang()));
    public static final Matcher<String> PASSWORD_TEXT =
            equalTo(getTranslation(PASSWD_UP, CONFIG.getLang()));

    public static final Matcher<String> MAIL_EMPTY_TEXT = equalTo(getTranslation(MAIL_EMPTY, CONFIG.getLang()));
    public static final Matcher<String> ONE_LETTER_TEXT =
            equalTo("1 " + getTranslation(MAIL_C1, CONFIG.getLang()));
    public static final Matcher<String> ONE_LETTER_FOLD_TEXT = equalTo("1");
    public static final Matcher<String> TWO_LETTERS_TEXT =
            equalTo("2 " + getTranslation(MAIL_C2, CONFIG.getLang()));

    public static final Matcher<String> FIVE_LETTERS_TEXT =
            equalTo("5 " + getTranslation(MAIL_C5, CONFIG.getLang()));

    public static final Matcher<String> ALIEN_PC_CHECKBOX_TEXT =
            equalTo(getTranslation(DO_NOT_REMEMBER, CONFIG.getLang()));

    public static final LinkInfo MAIL_OVER_ENTER_LINK = new LinkInfo(
            equalTo(getTranslation(TITLE, CONFIG.getLang())),
            equalTo(MAIL_PAGE_URL_HTTPS)
    );
}
