package ru.yandex.autotests.mordacom.data;

import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.language.Language;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_FIVE_LETTERS;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_NO_LETTERS;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_ONE_LETTER;
import static ru.yandex.autotests.utils.morda.auth.User.TURKEY_TWO_LETTERS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.HEAD_LOGOUT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.MAIL_LOGIN;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: leonsabr
 * Date: 13.01.12
 */
public class HeaderData {
    private static final Properties CONFIG = new Properties();

    public static final String MAIL_HREF = "https://mail.yandex.com/";
    public static final Matcher<String> MAIL_INBOX_URL_MATCHER =
            matches("\\Q" + MAIL_HREF + "\\E\\?uid=\\d+&login=[^&]+#inbox");

    public static final String PASSPORT_HREF = "https://passport.yandex.com/";
    public static final String PASSPORT_MODE_HREF = PASSPORT_HREF + "passport?mode=";

    private static final Matcher<String> MAIL_HREF_MATCHER =
            Matchers.equalTo(MAIL_HREF);

    public static LinkInfo getMailLink(Language language) {
        return new LinkInfo(
                Matchers.equalTo(getTranslation(MAIL_LOGIN, language)),
                MAIL_HREF_MATCHER);
    }

    public static LinkInfo getLogoutLink(Language language) {
        return new LinkInfo(
                Matchers.equalTo(getTranslation(HEAD_LOGOUT, language)),
                Matchers.startsWith(CONFIG.getBaseURL()),
                hasAttribute(HREF, Matchers.startsWith(PASSPORT_MODE_HREF + "logout")));
    }



    public static final LinkInfo MAIL_EMPTY_LINK = new LinkInfo(
            Matchers.equalTo("0"),
            MAIL_INBOX_URL_MATCHER,
            hasAttribute(HREF, MAIL_HREF_MATCHER)
    );

    public static final LinkInfo ONE_LETTERS_LINK = new LinkInfo(
            Matchers.equalTo("1"),
            MAIL_INBOX_URL_MATCHER,
            hasAttribute(HREF, MAIL_HREF_MATCHER)
    );

    public static final LinkInfo TWO_LETTERS_LINK = new LinkInfo(
            Matchers.equalTo("2"),
            MAIL_INBOX_URL_MATCHER,
            hasAttribute(HREF, MAIL_HREF_MATCHER)
    );

    public static final LinkInfo FIVE_LETTERS_LINK = new LinkInfo(
            Matchers.equalTo("5"),
            MAIL_INBOX_URL_MATCHER,
            hasAttribute(HREF, MAIL_HREF_MATCHER)
    );

    public static final List<Object[]> CNT_LETTERS_LINK = Arrays.asList(
            new Object[]{TURKEY_NO_LETTERS, MAIL_EMPTY_LINK},
            new Object[]{TURKEY_ONE_LETTER, ONE_LETTERS_LINK},
            new Object[]{TURKEY_TWO_LETTERS, TWO_LETTERS_LINK},
            new Object[]{TURKEY_FIVE_LETTERS, FIVE_LETTERS_LINK}
    );

    public static final Map<Language, Language> AVALIABLE_LANG = new HashMap<Language, Language>() {{
        put(Language.EN, Language.ID);
        put(Language.ID, Language.EN);
    }};
}
