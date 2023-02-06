package ru.yandex.autotests.turkey.data;

import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.LanguageMatcher.inLanguage;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Head.REGION;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Traffic.TURKEY_LABEL;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: ivannik
 * Date: 14.09.2014
 */
public class InformersData {
    private static final Properties CONFIG = new Properties();

    private static final String SEACH_URL = CONFIG.getProtocol() + "://yandex.com.tr/search/?";
    private static final String SEACH_WWW_URL = CONFIG.getProtocol() + "://www.yandex.com.tr/search/?";

    private static final String SERP_URL = CONFIG.getProtocol() + "://yandex\\.com\\.tr/search/\\?.*";
    private static final String SERP_WWW_URL = CONFIG.getProtocol() + "://www\\.yandex\\.com\\.tr/search/\\?.*";
    private static final String CURRENT_TEMPERATURE_FORMAT = "(0|(−?[1-9]\\d?)) °C";

    public static final LinkInfo REGION_LINK = new LinkInfo(
            equalTo(CONFIG.getBaseDomain().getCapital().getName()),
            startsWith(CONFIG.getProtocol() + "://yandex.com.tr/tune/geo/?retpath=" +
                    UrlManager.encodeRequest(CONFIG.getBaseURL())),
            hasAttribute(TITLE, equalTo(getTranslation(REGION, CONFIG.getLang())))
    );

    public static final LinkInfo WEATHER_LINK = new LinkInfo(
            matches(CURRENT_TEMPERATURE_FORMAT),
            allOf(matches(SERP_WWW_URL), containsString("text=%C4%B0stanbul%20hava%20durumu")),
            hasAttribute(TITLE, inLanguage(CONFIG.getLang()))
    );

    public static final LinkInfo TRAFFIC_LINK = new LinkInfo(
            containsString(getTranslation(TURKEY_LABEL, CONFIG.getLang())),
            allOf(matches(SERP_WWW_URL), containsString("text=%C4%B0stanbul%20trafik%20durumu"))
    );

    public static final LinkInfo USD_LINK = new LinkInfo(
            matches("\\$\\d,\\d{4}(↑|↓)"),
            allOf(matches(SERP_WWW_URL), containsString("text=usd%20d%C3%B6viz%20kuru")),
            hasAttribute(TITLE, matches("fiyat on \\d{1,2}/\\d{1,2} \\d{2}:\\d{2}")),
            hasAttribute(HREF, allOf(startsWith(SEACH_WWW_URL), containsString("text=usd%20d%C3%B6viz%20kuru")))
    );

    public static final LinkInfo EUR_LINK = new LinkInfo(
            matches("\\€\\d,\\d{4}(↑|↓)"),
            allOf(matches(SERP_WWW_URL), containsString("text=eur%20d%C3%B6viz%20kuru")),
            hasAttribute(TITLE, matches("fiyat on \\d{1,2}/\\d{1,2} \\d{2}:\\d{2}")),
            hasAttribute(HREF, allOf(startsWith(SEACH_WWW_URL), containsString("text=eur%20d%C3%B6viz%20kuru")))
    );
}
