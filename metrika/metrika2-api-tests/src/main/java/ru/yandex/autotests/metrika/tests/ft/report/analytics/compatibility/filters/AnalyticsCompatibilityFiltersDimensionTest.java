package ru.yandex.autotests.metrika.tests.ft.report.analytics.compatibility.filters;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.tests.ft.report.analytics.filters.AnalyticsFilterSyntaxBaseTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by sourx on 03.08.16.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры (google analytics): операторы для измерений (совместимость)")
@RunWith(Parameterized.class)
public class AnalyticsCompatibilityFiltersDimensionTest extends AnalyticsFilterSyntaxBaseTest {
    private final static String DIMENSION_SEARCH_PHRASE = "ym:s:searchPhrase";
    private final static String DIMENSION_SEARCH_ENGINE = "ym:s:searchEngineRoot";
    private final static String DIMENSION_GOAL = "ym:s:goal";
    private final static String DIMENSION_VISIT_PARAMS = "ym:s:paramsLevel1";
    private final static String DIMENSION_INTEREST = "ym:s:interest";
    private final static String DIMENSION_URL_PARAM = "ym:pv:URLParamName";
    private final static String DIMENSION_TRAFFIC_SOURCE = "ym:s:lastTrafficSource";
    private final static String DIMENSION_REFERER = "ym:s:referer";
    private final static String DIMENSION_VISIT_DURATION = "ym:s:visitDuration";

    private final static String METRIC_VISIT = "ym:s:visits";
    private final static String METRIC_HIT = "ym:pv:pageviews";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION_SEARCH_PHRASE, METRIC_VISIT, dimension(DIMENSION_SEARCH_ENGINE).equalTo("google")},
                {DIMENSION_SEARCH_PHRASE, METRIC_VISIT, dimension(DIMENSION_SEARCH_ENGINE).notEqualTo("google")},
                {DIMENSION_SEARCH_PHRASE, METRIC_VISIT, dimension(DIMENSION_SEARCH_ENGINE).matchRegEx(".*")},
                {DIMENSION_SEARCH_PHRASE, METRIC_VISIT, dimension(DIMENSION_SEARCH_ENGINE).notMatchRegEx(".*")},
                {DIMENSION_SEARCH_PHRASE, METRIC_VISIT, dimension(DIMENSION_SEARCH_ENGINE).matchSubstring("goo")},
                {DIMENSION_SEARCH_PHRASE, METRIC_VISIT, dimension(DIMENSION_SEARCH_ENGINE).matchStar("*")},
                {DIMENSION_SEARCH_PHRASE, METRIC_VISIT, dimension(DIMENSION_SEARCH_ENGINE).notMatchStar("*")},
                {DIMENSION_SEARCH_PHRASE, METRIC_VISIT, dimension(DIMENSION_SEARCH_ENGINE).notMatchSubstring("goo")},
                {DIMENSION_SEARCH_PHRASE, METRIC_VISIT, dimension(DIMENSION_SEARCH_ENGINE).greaterThan("google")},
                {DIMENSION_SEARCH_PHRASE, METRIC_VISIT, dimension(DIMENSION_SEARCH_ENGINE).greaterThanOrEqualTo("google")},
                {DIMENSION_SEARCH_PHRASE, METRIC_VISIT, dimension(DIMENSION_SEARCH_ENGINE).lessThan("google")},
                {DIMENSION_SEARCH_PHRASE, METRIC_VISIT, dimension(DIMENSION_SEARCH_ENGINE).lessThanOrEqualTo("google")},

                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).equalTo(COUNTER.get(Counter.GOAL_ID))},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).notEqualTo(COUNTER.get(Counter.GOAL_ID))},

                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).notMatchStar("*")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).notEqualTo("category")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).notMatchSubstring("cat")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).notMatchRegEx(".*")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).lessThan("category")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).lessThanOrEqualTo("category")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).matchStar("*")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("category")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).matchSubstring("cat")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).matchRegEx(".*")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).greaterThan("category")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).greaterThanOrEqualTo("category")},

                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).notEqualTo("literature")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).equalTo("literature")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).greaterThan("cinema")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).lessThan("cinema")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).greaterThanOrEqualTo("cinema")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).lessThanOrEqualTo("cinema")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).matchSubstring("cine")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).notMatchSubstring("cine")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).matchRegEx(".*")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).notMatchRegEx(".*")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).matchStar("*")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).notMatchStar("*")},

                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).notMatchStar("h*")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).notEqualTo("hid")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).notMatchSubstring("hid")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).notMatchRegEx(".*")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).lessThan("hid")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).lessThanOrEqualTo("hid")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).matchStar("*")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("hid")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).matchSubstring("hid")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).matchRegEx(".*")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).greaterThan("hid")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).greaterThanOrEqualTo("hid")},

                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).equalTo("organic")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).notEqualTo("organic")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).greaterThan("ad")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).lessThan("ad")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).greaterThanOrEqualTo("ad")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).lessThanOrEqualTo("ad")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).matchSubstring("org")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).notMatchSubstring("org")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).matchRegEx(".*")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).notMatchRegEx(".*")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).matchStar("*")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).notMatchStar("*")},

                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).notMatchStar("*ya*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).notEqualTo("http://market.yandex.ru/")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).notMatchSubstring("market")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).notMatchRegEx(".*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).lessThan("http://market.yandex.ru/")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).lessThanOrEqualTo("http://market.yandex.ru/")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).equalTo("http://market.yandex.ru/")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchSubstring("market")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchRegEx(".*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).greaterThan("http://market.yandex.ru/")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).greaterThanOrEqualTo("http://market.yandex.ru/")},

                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).notEqualTo(0)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).lessThan(10)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).lessThanOrEqualTo(10)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).equalTo(0)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).greaterThan(10)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).greaterThanOrEqualTo(10)}
        });
    }
}
