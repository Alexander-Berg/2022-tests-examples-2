package ru.yandex.autotests.turkey.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.utils.morda.language.Dictionary;

import static java.lang.String.format;
import static org.hamcrest.CoreMatchers.endsWith;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Error404.CONTACT_US;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Error404.NO_PAGE_FULL;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Error404.SPECIAL_BAD_3;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff
 * Date: 07.02.13
 */
public class Page404Data {
    private static final Properties CONFIG = new Properties();

    private static final String SEARCH_URL_PATTERN = "https://yandex%s/search/?msid=";
    private static final String COMPANY_LINK_HREF = "https://yandex.com.tr/sirket/";
    private static final String COMPANY_LINK_URL = "://yandex.com.tr/company/";

    public static final String PAGE_404_URL = CONFIG.getBaseURL() + "/sl/blah";

    public static final Matcher<String> SEARCH_BUTTON_TEXT_MATCHER =
            equalTo(getTranslation("home", "error-handlers", "Найти", CONFIG.getLang()));

    public static final String REQUEST = "javascript здесь";
    public static final Matcher<String> YANDEX_TEXT = equalTo("Yandex");
    public static final Matcher<String> SEARCH_URL = startsWith(String.format(SEARCH_URL_PATTERN, CONFIG.getBaseDomain()));

    public static final Matcher<String> NO_PAGE_TEXT = equalTo(getTranslation(NO_PAGE_FULL, CONFIG.getLang()));

    public static final String CONTACT_TEXT = getTranslation(CONTACT_US, CONFIG.getLang());

    public static final Matcher<String> FEEDBACK_MESSAGE =
            equalTo(format(getTranslation(SPECIAL_BAD_3, CONFIG.getLang()).replace("  ", " "), CONTACT_TEXT));

    public static final Matcher<String> FEEDBACK_URL = allOfDetailed(
            startsWith("https://yandex.com.tr/support/not-found/?form1969-url404="),
            endsWith("&form1969-fromurl404="));

    public static final LinkInfo COMPANY_LINK = new LinkInfo(
            equalTo("About"),
            startsWith("https://yandex.com/company"),
            hasAttribute(HREF, equalTo("https://yandex.com/company/"))
    );

    public static final LinkInfo SIRKET_LINK = new LinkInfo(
            equalTo(getTranslation(Dictionary.Home.Foot.COMPANY_NOM, CONFIG.getLang())),
            equalTo(COMPANY_LINK_HREF),
            HtmlAttributeMatcher.hasAttribute(HREF, equalTo(COMPANY_LINK_HREF))
    );

    public static final LinkInfo YANDEX_LINK = new LinkInfo(
            YANDEX_TEXT,
            equalTo(CONFIG.getProtocol() + "://yandex.com.tr/")
    );

}
