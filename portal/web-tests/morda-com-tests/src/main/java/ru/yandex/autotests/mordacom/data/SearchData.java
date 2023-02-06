package ru.yandex.autotests.mordacom.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import java.util.Arrays;
import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.SEARCH;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encodeRequest;

/**
 * User: leonsabr
 * Date: 24.08.2010
 */
public class SearchData {
    private static final Properties CONFIG = new Properties();

    public static Matcher<String> getSearchButtonTextMatcher(Language language) {
        return equalTo(getTranslation(SEARCH, language));
    }

    public static final List<String> SEARCH_TEST_DATA =
            Arrays.asList("hi");//, "курс доллара", "gaga", "я", "");
    public static final List<String> SUGGEST_TESTS = Arrays.asList("hi", "курс доллара", "gaga", "я");

    public static final String TUNE_SUGGEST_PAGE_URL = "http://tune.yandex.com/suggest/?retpath=" +
            UrlManager.encode(CONFIG.getBaseURL()) + "%2F%3Fdomredir%3D1";

    public static final String SEARCH_REQUEST = "yandex world maps";
    public static final String ENCODED_REQUEST = encodeRequest(SEARCH_REQUEST);

    public static final String COM_SEARCH_URL = "https://www.yandex.com/search/";
}