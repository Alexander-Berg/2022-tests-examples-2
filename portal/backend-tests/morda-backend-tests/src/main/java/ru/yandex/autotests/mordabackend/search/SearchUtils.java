package ru.yandex.autotests.mordabackend.search;

import ru.yandex.autotests.mordabackend.Properties;
import ru.yandex.autotests.mordabackend.useragents.UserAgent;
import ru.yandex.autotests.mordaexportsclient.beans.SearchPromolinkEntry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import java.util.*;

import static ru.yandex.autotests.mordabackend.useragents.UserAgent.*;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.*;
import static ru.yandex.autotests.utils.morda.language.Language.*;
import static ru.yandex.autotests.utils.morda.region.Region.*;
import static ru.yandex.autotests.utils.morda.url.Domain.COM_TR;

/**
 * User: ivannik
 * Date: 25.07.2014
 */
public class SearchUtils {

    public static final Properties CONFIG = new Properties();
    public static final String SEARCH_URL_PATTERN = "%s://yandex%s/search%s";
    public static final String COMTR_SEARCH_URL_PATTERN = "%s://www.yandex.com.tr/search%s";

    public static final List<Language> LANGUAGES = Arrays.asList(RU, UK, BE, KK, TT);
    public static final List<Region> SEARCH_REGIONS_MAIN = Arrays.asList(MOSCOW, KIEV, SANKT_PETERBURG,
            SAMARA, MINSK, CHELYABINSK, NOVOSIBIRSK, KAZAN, NIZHNIY_NOVGOROD, VOLGOGRAD, LYUDINOVO);


    public static final List<Region> SEARCH_REGIONS_TR = Arrays.asList(ISTANBUL, IZMIR, BURSA, ANKARA);

    public static final List<Region> SEARCH_REGIONS_ALL = new ArrayList<>();
    static {
        SEARCH_REGIONS_ALL.addAll(SEARCH_REGIONS_MAIN);
        SEARCH_REGIONS_ALL.addAll(SEARCH_REGIONS_TR);
    }

    public static final String SEARCH_REQUEST = "javascript здесь";

    public static final Map<UserAgent, MordaExport<SearchPromolinkEntry>> USER_AGENT_EXPORTS =
            new HashMap<UserAgent, MordaExport<SearchPromolinkEntry>>() {{
                put(IOS_IPAD, SEARCH_PROMOLINK_IPAD);
                put(ANDROID_LG, null);
                put(TOUCH, null);
                put(FF_34, SEARCH_PROMOLINK);
                put(CHROME_OSX_35, SEARCH_PROMOLINK);
                put(ANDROID_SAMS_TAB, SEARCH_PROMOLINK_ANDROID_PAD);
            }};

    public static final List<UserAgent> USER_AGENTS = new ArrayList<>(USER_AGENT_EXPORTS.keySet());

    public static String getSearchRequest(String request) {
        return "?text=" + UrlManager.encodeRequest(request);
    }

    public static String getSearchLink(UserAgent userAgent, Domain domain) {
        if (userAgent.getIsTouch() == 1 && userAgent.getIsTablet() == 0) {
            return domain.equals(COM_TR) ?
                    String.format(COMTR_SEARCH_URL_PATTERN, CONFIG.getProtocol(), "/touch/") :
                    String.format(SEARCH_URL_PATTERN, CONFIG.getProtocol(), domain.getValue(), "/touch/");
        } else if (userAgent.getIsTablet() == 1) {
            return domain.equals(COM_TR) ?
                    String.format(COMTR_SEARCH_URL_PATTERN, CONFIG.getProtocol(), "/pad/") :
                    String.format(SEARCH_URL_PATTERN, CONFIG.getProtocol(), domain.getValue(), "/pad/");
        } else {
            return domain.equals(COM_TR) ?
                    String.format(COMTR_SEARCH_URL_PATTERN, CONFIG.getProtocol(), "/") :
                    String.format(SEARCH_URL_PATTERN, CONFIG.getProtocol(), domain.getValue(), "/");
        }
    }}
