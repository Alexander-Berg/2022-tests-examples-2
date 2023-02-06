package ru.yandex.autotests.turkey.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.turkey.Properties;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.COMPANY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.LEGAL;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: leonsabr
 * Date: 04.10.12
 */
public class FooterData {
    private static final Properties CONFIG = new Properties();

    private static final String COMPANY_LINK_URL = "https://yandex.com.tr/company/";
    private static final String COMPANY_LINK_HREF = "https://yandex.com.tr/sirket/";
    private static final String FEEDBACK_LINK_HREF = CONFIG.getProtocol() + "://contact2.yandex.com.tr/";
    private static final String FEEDBACK_LINK_URL = CONFIG.getProtocol() + "://yandex.com.tr/support";
    private static final String LEGAL_LINK_HREF = CONFIG.getProtocol() + "://yandex.com.tr/legal/confidential/";
    private static final String DEFAULT_SEARCH_LINK_HREF = "https://yandex.com.tr/kullan?from=morda_new";
    private static final String DEFAULT_SEARCH_LINK_URL = "https://yandex.com.tr/kullan/?from=morda_new";
    private static final String SERVICES_LINK_HREF = fromUri(CONFIG.getProtocol() + "://yandex.com.tr")
                                .path("/all")
                                .build()
                                .toString();

    public static final LinkInfo COMPANY_LINK = new LinkInfo(
            equalTo(getTranslation(COMPANY, CONFIG.getLang())),
            startsWith(COMPANY_LINK_HREF),
            HtmlAttributeMatcher.hasAttribute(HREF, equalTo(COMPANY_LINK_HREF))
    );

    public static final LinkInfo FEEDBACK_LINK = new LinkInfo(
            equalTo(getTranslation("home","foot","help", CONFIG.getLang())),
            startsWith(FEEDBACK_LINK_URL)
    );

    public static final LinkInfo LEGAL_LINK = new LinkInfo(
            equalTo(getTranslation(LEGAL, CONFIG.getLang())),
            startsWith(LEGAL_LINK_HREF),
            hasAttribute(HREF, equalTo(LEGAL_LINK_HREF))
    );
    
//    public static final LinkInfo SERVICES_LINK = new LinkInfo(
//            equalTo(getTranslation(SERVICES, CONFIG.getLang())),
//            startsWith(SERVICES_LINK_HREF),
//            hasAttribute(HREF, equalTo(SERVICES_LINK_HREF))
//    );

    public static final LinkInfo DEFAULT_SEARCH_LINK = new LinkInfo(
            equalTo(getTranslation("home", "foot", "using", CONFIG.getLang())),
            startsWith(DEFAULT_SEARCH_LINK_URL),
            hasAttribute(HREF, equalTo(DEFAULT_SEARCH_LINK_HREF))
    );

    public static final Matcher<String> COPYRIGHT_TEXT_MATCHER = equalTo("© Yandex");
}
