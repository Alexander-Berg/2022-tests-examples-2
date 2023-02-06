package ru.yandex.autotests.mainmorda.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import java.util.Arrays;
import java.util.List;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SearchForm.CAP_FIND_EVERYTHING;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.FOR_BY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Main.FOR_KZ;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.DomainManager.getMasterDomain;

/**
 * User: alex89, leonsabr
 * Date: 24.04.12
 */
public class SearchData {
    public static final Properties CONFIG = new Properties();

    public static final Matcher<String> EXAMPLE_TEXT = startsWith(getTranslation(CAP_FIND_EVERYTHING, CONFIG.getLang()) + ".");

    public static final String SEARCH_URL_PATTERN = "https?://yandex\\%s/search/\\?lr=.*";
    public static final Matcher<String> SEARCH_URL =
            matches(String.format(SEARCH_URL_PATTERN, CONFIG.getBaseDomain()));
    public static final String BETA_SEARCH_URL_PATTERN = "https?://beta\\.yandex\\%s/search/\\?lr=.*";
    public static final Matcher<String> BETA_SEARCH_URL =
            matches(String.format(BETA_SEARCH_URL_PATTERN, CONFIG.getBaseDomain()));

    public static final String BETA_URL = CONFIG.getBaseURL().replace("www", "beta");

    public static final String FAMILY_SEARCH_URL = CONFIG.getBaseURL().replace("www", "family");
    public static final Matcher<String> FAMILY_PARAMETER_MATCHER = allOf(SEARCH_URL, containsString("family=yes"));

    public static final String TUNE_SUGGEST_PAGE_URL = "http://tune.yandex.ru/suggest/?retpath=" +
            UrlManager.encodeRetpath(CONFIG.getBaseURL()) + "%2F%3Fdomredir%3D1";
    public static final String TUNE_PAGE_URL = "http://tune.yandex.ru/";

    public static final List<String> SUGGEST_TESTS = Arrays.asList("mp3 скачать", "курс доллара",
            "gaga", "я");

    public static final Matcher<String> COUNTRY_TEXT;

    static {
        if (CONFIG.domainIs(KZ)) {
            COUNTRY_TEXT = equalTo(getTranslation(FOR_KZ, CONFIG.getLang()));
        } else if (CONFIG.domainIs(BY)) {
            COUNTRY_TEXT = equalTo(getTranslation(FOR_BY, CONFIG.getLang()));
        } else {
            COUNTRY_TEXT = null;
        }
    }

    public static final String REQUEST_TEXT = "cat";

    public static final String REDIRECT_TEXT = "javascript здесь";


    public static final String REDIRECT_URL_PATTERN = CONFIG.getMordaEnv() + ".yandex%s/%s?text="
            + REDIRECT_TEXT;

    public static final Matcher<String> REDIRECT_EXPECTED_URL_MATCHER =
            containsString("text=" + UrlManager.encodeRequest(REDIRECT_TEXT));

    public static enum SearchType {
        YANDSEARCH("yandsearch"),
        MSEARCH("msearch"),
        TOUCHSEARCH("touchsearch"),
        TELSEARCH("telsearch");

        public String search;

        private static final String EXPECTED_URL_PATTERN = "http://yandex%s/yandsearch";
        private static final String EXPECTED_URL_PATTERN_COM = "http://%s.yandex%s/yandsearch";

        private SearchType(String search) {
            this.search = search;
        }

        public String getSearch() {
            return search;
        }

        public static String getExpectedUrl(SearchType searchType, Domain domain) {
            Domain searchDomain = getSearchDomain(searchType, domain);
            if (domain.equals(Domain.COM) || domain.equals(Domain.COM_TR)) {
                return String.format(EXPECTED_URL_PATTERN_COM, CONFIG.getMordaEnv(),
                        searchDomain);
            }
            return String.format(EXPECTED_URL_PATTERN, searchDomain);
        }

        public static Domain getSearchDomain(SearchType searchType, Domain domain) {
            return searchType.equals(YANDSEARCH) ? domain : getMasterDomain(domain);
        }
    }
}
