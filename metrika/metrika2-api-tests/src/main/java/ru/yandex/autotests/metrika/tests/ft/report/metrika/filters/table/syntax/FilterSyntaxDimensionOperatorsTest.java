package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by konkov on 12.05.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: операторы для измерений")
@RunWith(Parameterized.class)
public class FilterSyntaxDimensionOperatorsTest extends FilterSyntaxBaseTest {
    private final static String DIMENSION_GOAL = "ym:s:goal";
    private final static String DIMENSION_VISIT_PARAMS = "ym:s:paramsLevel1";
    private final static String DIMENSION_INTEREST = "ym:s:interest";
    private final static String DIMENSION_URL_PARAM = "ym:pv:URLParamName";
    private final static String DIMENSION_TRAFFIC_SOURCE = "ym:s:lastTrafficSource";
    private final static String DIMENSION_TRAFFIC_SOURCE_NAME = "ym:s:lastTrafficSourceName";
    private final static String DIMENSION_REFERER = "ym:s:referer";
    private final static String DIMENSION_DOMAIN = "ym:s:startURLDomain";
    private final static String DIMENSION_VISIT_DURATION = "ym:s:visitDuration";
    private final static String DIMENSION_DATE = "ym:pv:date";
    private final static String DIMENSION_DEVICE_CATEGORY_NAME = "ym:pv:deviceCategoryName";

    private final static String METRIC_VISIT = "ym:s:visits";
    private final static String METRIC_HIT = "ym:pv:pageviews";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).equalTo(COUNTER.get(Counter.GOAL_ID))},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).in(COUNTER.get(Counter.GOAL_ID))},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).in(COUNTER.get(Counter.GOAL_ID), COUNTER.get(Counter.GOAL_ID))},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).notIn(COUNTER.get(Counter.GOAL_ID), COUNTER.get(Counter.GOAL_ID))},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).notEqualTo(COUNTER.get(Counter.GOAL_ID))},

                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).notMatchStar("*")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).notEqualTo("category")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).notMatchSubstring("cat")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).notMatchRegEx(".*")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).lessThan("category")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).lessThanOrEqualTo("category")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).matchStar("*")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("category")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).in("category")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).in("category", "level")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).notIn("category", "level")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).matchSubstring("cat")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).matchRegEx(".*")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).greaterThan("category")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).greaterThanOrEqualTo("category")},

                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).notEqualTo("literature")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).equalTo("literature")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).in("literature")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).in("literature", "cinema")},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).notIn("literature", "cinema")},
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
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).in("hid")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).in("hid", "gid")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).notIn("hid", "gid")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).matchSubstring("hid")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).matchRegEx(".*")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).greaterThan("hid")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).greaterThanOrEqualTo("hid")},

                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).equalTo("organic")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).in("organic")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).in("organic", "ad")},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).notIn("organic", "ad")},
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

                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).equalTo("Переходы из поисковых систем")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).in("Переходы из поисковых систем")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).in("Переходы из поисковых систем", "Переходы по рекламе")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).notIn("Переходы из поисковых систем", "Переходы по рекламе")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).notEqualTo("Переходы из поисковых систем")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).greaterThan("Переходы по рекламе")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).lessThan("Переходы по рекламе")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).greaterThanOrEqualTo("Переходы по рекламе")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).lessThanOrEqualTo("Переходы по рекламе")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).matchSubstring("org")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).notMatchSubstring("org")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).matchRegEx(".*")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).notMatchRegEx(".*")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).matchStar("*")},
                {DIMENSION_TRAFFIC_SOURCE_NAME, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE_NAME).notMatchStar("*")},

                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).notMatchStar("*ya*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).notEqualTo("http://market.yandex.ru/")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).notMatchSubstring("market")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).notMatchRegEx(".*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).lessThan("http://market.yandex.ru/")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).lessThanOrEqualTo("http://market.yandex.ru/")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).equalTo("http://market.yandex.ru/")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).in("http://market.yandex.ru/")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).in("http://market.yandex.ru/", "http://google.com")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).notIn("http://market.yandex.ru/", "http://google.com")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchSubstring("market")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchRegEx(".*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).greaterThan("http://market.yandex.ru/")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).greaterThanOrEqualTo("http://market.yandex.ru/")},

                // плохая регулярка в match star
                // оптимизатор запроса работает на основе регулярок, и должен экранировать все спецсимволы регулярок в исходном выражении
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*[*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).notMatchStar("*ya*[*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*]*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*(*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*)*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*{*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*}*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*-*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*?*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*+*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*^*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*$*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*&*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*|*")},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya*~*")},
                // METR-25279
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_DOMAIN).matchStar("*\\'*doska-les**russkiy-sort-av*russkiy-av*russkiy-strogannaya*les-vagonka*russkiy-les*\\'")},
                // metr-25278
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).matchStar("*ya\"*")},

                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).notEqualTo(0)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).lessThan(10)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).lessThanOrEqualTo(10)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).equalTo(0)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).in(0)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).in(0, 1)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).notIn(0, 1)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).greaterThan(10)},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).greaterThanOrEqualTo(10)},

                // METR-30971
                {DIMENSION_DATE, METRIC_HIT, dimension(DIMENSION_DEVICE_CATEGORY_NAME).equalTo("Планшеты")},
                {DIMENSION_DATE, METRIC_HIT, dimension(DIMENSION_DEVICE_CATEGORY_NAME).equalTo("ПК")},
                {DIMENSION_DATE, METRIC_HIT, dimension(DIMENSION_DEVICE_CATEGORY_NAME).equalTo("ТВ")},
        });
    }
}
