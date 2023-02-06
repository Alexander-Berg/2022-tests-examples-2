package ru.yandex.autotests.mordamobile.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordamobile.Properties;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.MAIL_C1_MOBILE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.MAIL_C2_MOBILE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.MAIL_C5_MOBILE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.*;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 18.04.13
 */
public class MailData {
    private static final Properties CONFIG = new Properties();

    public static final Matcher<String> TITLE = equalTo(getTranslation(MAIL_TITLE, CONFIG.getLang()));
    public static final Matcher<String> LOGIN_TEXT = equalTo(getTranslation(MAIL_LOGIN, CONFIG.getLang()));

    public static final Matcher<String> MAIL_HREF =
            equalTo("https://passport.yandex.ru/registration?mode=register&" +
                    "retpath=https%3A%2F%2Fmail.yandex.ru&from=mail&origin=home_touch");

    public static final Matcher<String> MAIL_URL = MAIL_HREF;

    public static final LinkInfo MAIL_LINK = new LinkInfo(
            not(""),
            startsWith(CONFIG.getBaseURL()),
            hasAttribute(HREF, equalTo("https://mail.yandex.ru/"))
    );

    public static final Matcher<String> MAIL_EMPTY_TEXT = equalTo(getTranslation(MAIL_EMPTY_MOBILE, CONFIG.getLang()));
    public static final Matcher<String> ONE_LETTER_TEXT =
            equalTo("1\n" + getTranslation(MAIL_C1_MOBILE, CONFIG.getLang()));
    public static final Matcher<String> TWO_LETTERS_TEXT =
            equalTo("2\n" + getTranslation(MAIL_C2_MOBILE, CONFIG.getLang()));

    public static final Matcher<String> FIVE_LETTERS_TEXT =
            equalTo("5\n" + getTranslation(MAIL_C5_MOBILE, CONFIG.getLang()));

    public static final Matcher<String> DOMIK_TITLE_MATCHER = equalTo(getTranslation(DOMIK_TITLE, CONFIG.getLang()));
    public static final String EMPTY_STRING = "";

    public static final LinkInfo REMIND_PASSWORD_LINK = new LinkInfo(
            equalTo(getTranslation(DOMIK_REMEMBER_PWD, CONFIG.getLang())),
            equalTo("https://passport.yandex.ru/passport?mode=restore")
    );

    public static final LinkInfo REGISTER_LINK = new LinkInfo(
            equalTo(getTranslation(DOMIK_REGISTER, CONFIG.getLang())),
            MAIL_URL,
            hasAttribute(HREF, MAIL_HREF)
    );

    public static final String LOGGED_MAIL_URL = "https://mail.yandex.ru/touch";
}
