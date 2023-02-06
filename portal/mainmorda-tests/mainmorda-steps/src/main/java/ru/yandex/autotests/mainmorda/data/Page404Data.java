package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import static java.lang.String.format;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static org.hamcrest.text.IsEmptyString.isEmptyString;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: eoff
 * Date: 07.02.13
 */
public class Page404Data {
    private static final Properties CONFIG = new Properties();

    private static final String SEARCH_URL_PATTERN = "https?://yandex\\%s/search/.*";
    private static final String COMPANY_RU_LINK_HREF = CONFIG.getProtocol() + "://company.yandex.ru/";
    private static final String COMPANY_COM_LINK_HREF = CONFIG.getProtocol() + "://company.yandex.com/";

    public static final String PAGE_404_URL_PART = "/sl/blabla";
    public static final String PAGE_404_URL = CONFIG.getBaseURL() + PAGE_404_URL_PART;

    public static final Matcher<String> SEARCH_BUTTON_TEXT_MATCHER =
            equalTo(getTranslation("home", "error-handlers", "Найти", CONFIG.getLang()));

    public static final String REQUEST = "javascript здесь";
    public static final Matcher<String> ERROR_CODE_MATCHER = equalTo("404");
    public static final Matcher<String> YANDEX_TEXT_RU = equalTo("Яндекс");
    public static final Matcher<String> YANDEX_TEXT_EN = equalTo("Yandex");
    public static final Matcher<String> LOGO_HREF_MATCHER = equalTo(CONFIG.getProtocol() + "://www.yandex" + CONFIG.getBaseDomain() + "/");
    public static final Matcher<String> SEARCH_URL = matches(format(SEARCH_URL_PATTERN, CONFIG.getBaseDomain()));

    public static final Matcher<String> NO_PAGE_TEXT =
            equalTo(getTranslation("home", "error404", "nopage_full", CONFIG.getLang()).trim());

    public static final Matcher<String> FEEDBACK_URL =
            Matchers.equalTo(format("https://yandex%s/support/not-found/?form1969-url404=%s&form1969-fromurl404=",
                    CONFIG.getBaseDomain(), UrlManager.encode(PAGE_404_URL)));

    public static final LinkInfo COMPANY_RU_LINK = new LinkInfo(
            equalTo(getTranslation("home", "error500", "about", CONFIG.getLang())),
            startsWith(COMPANY_RU_LINK_HREF),
            hasAttribute(HREF, equalTo(COMPANY_RU_LINK_HREF)),
            hasAttribute(TITLE, isEmptyString())
    );

    public static final LinkInfo COMPANY_COM_LINK = new LinkInfo(
            equalTo(getTranslation("home", "error500", "about", Language.EN)),
            startsWith(COMPANY_COM_LINK_HREF),
            hasAttribute(HREF, equalTo(COMPANY_COM_LINK_HREF)),
            hasAttribute(TITLE, isEmptyString())
    );

    public static final LinkInfo YANDEX_LINK = new LinkInfo(
            YANDEX_TEXT_RU,
            startsWith(CONFIG.getProtocol() + "://www.yandex" + CONFIG.getBaseDomain() + "/")
    );

    public static final Matcher<String> COPYRIGHT_TEXT_MATCHER = equalTo("© 2001-2015 «Яндекс»");
}
