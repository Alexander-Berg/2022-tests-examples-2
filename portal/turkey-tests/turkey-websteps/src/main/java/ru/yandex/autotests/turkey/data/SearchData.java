package ru.yandex.autotests.turkey.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import java.util.Arrays;
import java.util.List;

import static org.hamcrest.CoreMatchers.allOf;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.region.Region.ADANA;
import static ru.yandex.autotests.utils.morda.region.Region.ANKARA;
import static ru.yandex.autotests.utils.morda.region.Region.ANTALYA;
import static ru.yandex.autotests.utils.morda.region.Region.BURSA;
import static ru.yandex.autotests.utils.morda.region.Region.GAZIANTEP;
import static ru.yandex.autotests.utils.morda.region.Region.ISTANBUL;
import static ru.yandex.autotests.utils.morda.region.Region.IZMIR;
import static ru.yandex.autotests.utils.morda.region.Region.KAYSERI;
import static ru.yandex.autotests.utils.morda.region.Region.KONYA;
import static ru.yandex.autotests.utils.morda.region.Region.MERSIN;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encodeRequest;

/**
 * User: leonsabr
 * Date: 05.10.12
 */
public class SearchData {
    private static final Properties CONFIG = new Properties();

    public static final String FAMILY_SEARCH_URL = CONFIG.getBaseURL().replaceFirst("www", "aile");

    public static final Matcher<String> FAMILY_SEARCH_PARAMETER_MATCHER = allOf(
            matches("https?://aile.yandex\\.com\\.tr/search/.*"),
            containsString("family=yes"));
    public static final Matcher<String> FAMILY_TABS_PARAMETER_MATCHER =
            anyOf(containsString("family=1"), containsString("family%3D1"));

    public static final List<Region> LR_TEST_DATA =
            Arrays.asList(ISTANBUL, ANKARA, IZMIR, BURSA, ADANA, GAZIANTEP, KONYA, ANTALYA, KAYSERI, MERSIN);

    public static final List<String> SEARCH_TEST_DATA =
            Arrays.asList("Alanya", "Atatürk", "best hotels", "");
    public static final List<String> SUGGEST_TESTS = Arrays.asList("Alanya", "Atatürk", "best hotels");

    public static final String TUNE_SUGGEST_PAGE_URL = "http://tune.yandex.com.tr/suggest/?retpath=" +
                    UrlManager.encode(CONFIG.getBaseURL()) + "%2F%3Fdomredir%3D1";

    public static final String EXTERNAL_TURKEY_LR = "11508";
    public static final Matcher<String> LR_EXTERNAL_URL_MATCHER = containsString("lr=" + EXTERNAL_TURKEY_LR);

    public static Matcher<String> getLrUrlMatcher(Region region) {
        return containsString("lr=" + region.getRegionId());
    }

    public static final String SEARCH_REQUEST = "yandex reklam";
    public static final String ENCODED_REQUEST = encodeRequest(SEARCH_REQUEST);

    public static final Matcher<String> COM_TR_SEARCH_URL = matches("https?://www\\.yandex\\.com\\.tr/search/.*");
}
