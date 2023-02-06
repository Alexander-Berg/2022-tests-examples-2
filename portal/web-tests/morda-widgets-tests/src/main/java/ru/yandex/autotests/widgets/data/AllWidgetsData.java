package ru.yandex.autotests.widgets.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.widgets.Properties;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.utils.morda.url.Domain.BY;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.RU;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * User: leonsabr
 * Date: 14.11.11
 */
public class AllWidgetsData {
    private static final Properties CONFIG = new Properties();
    public static final String WIDGETS_PATTERN = CONFIG.getProtocol() + "://%s.yandex%s";

    private static final List<String> RU_REGIONS = Arrays.asList("10174", "1", "225");

    private static final List<String> UA_REGIONS = Arrays.asList("187", "20544");

    private static final List<String> BY_REGIONS = Arrays.asList("157", "29630", "149");

    private static final List<String> KZ_REGIONS = Arrays.asList("163", "29403", "159");

    private static final Map<Domain, List<String>> RELEVANT_REGIONS = new HashMap<Domain, List<String>>() {{
        put(RU, RU_REGIONS);
        put(UA, UA_REGIONS);
        put(BY, BY_REGIONS);
        put(KZ, KZ_REGIONS);
    }};

    public static Matcher<String> getRegionMatcher(Domain domain) {
        ArrayList<Matcher<String>> matchers = new ArrayList<Matcher<String>>();
        for (String str : RELEVANT_REGIONS.get(domain)) {
            matchers.add(containsString("?region=" + str));
        }
        return anyOf(matchers.toArray(new Matcher[matchers.size()]));
    }
}
