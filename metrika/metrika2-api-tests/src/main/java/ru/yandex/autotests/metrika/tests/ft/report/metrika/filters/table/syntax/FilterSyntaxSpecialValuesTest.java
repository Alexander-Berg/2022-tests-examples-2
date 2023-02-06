package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by konkov on 02.07.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: специальные символы в аргументах операторов")
@RunWith(Parameterized.class)
public class FilterSyntaxSpecialValuesTest extends FilterSyntaxBaseTest {
    private final static String DIMENSION_VISIT_PARAMS = "ym:s:paramsLevel1";
    private final static String DIMENSION_URL_PARAM = "ym:pv:URLParamName";
    private final static String DIMENSION_INTEREST = "ym:s:interest";
    private final static String DIMENSION_TRAFFIC_SOURCE = "ym:s:lastTrafficSource";
    private final static String DIMENSION_REFERER = "ym:s:referer";
    private final static String DIMENSION_DATE = "ym:pv:date";
    private final static String DIMENSION_DEVICE_CATEGORY_NAME = "ym:pv:deviceCategoryName";

    private final static String METRIC_SUM_PARAMS = "ym:s:sumParams";
    private final static String METRIC_VISIT = "ym:s:visits";
    private final static String METRIC_HIT = "ym:pv:pageviews";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("\\")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("'")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("\"")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("\0")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("\b")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("\t")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("\n")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("\f")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("\r")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("\r\n")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("\n\r")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).equalTo("\uFFFF")},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).in("category", null)},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).in("category", "level", null)},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).notIn("category", null)},
                {DIMENSION_VISIT_PARAMS, METRIC_VISIT, dimension(DIMENSION_VISIT_PARAMS).notIn("category", "level", null)},

                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("\\")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("'")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("\"")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("\0")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("\b")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("\t")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("\n")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("\f")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("\r")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("\r\n")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("\n\r")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).equalTo("\uFFFF")},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).in("hid", null)},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).in("hid", "gid", null)},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).notIn("hid", null)},
                {DIMENSION_URL_PARAM, METRIC_HIT, dimension(DIMENSION_URL_PARAM).notIn("hid", "gid", null)},

                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("1")},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo(1)},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).lessThan(0)},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).greaterThan(0)},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo(-1)},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo(2.5)},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).lessThanOrEqualTo(1e10)},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).greaterThanOrEqualTo(1e-10)},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).lessThanOrEqualTo(-1e-10)},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).greaterThanOrEqualTo(-1e10)},

                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).in("literature", null)},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).in("literature", "cinema", null)},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).notIn("literature", null)},
                {DIMENSION_INTEREST, METRIC_VISIT, dimension(DIMENSION_INTEREST).notIn("literature", "cinema", null)},

                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).in("organic", null)},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).in("organic", "ad", null)},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).notIn("organic", null)},
                {DIMENSION_TRAFFIC_SOURCE, METRIC_VISIT, dimension(DIMENSION_TRAFFIC_SOURCE).notIn("organic", "ad", null)},

                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).in("http://market.yandex.ru/", null)},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).in("http://market.yandex.ru/", "http://google.com", null)},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).notIn("http://market.yandex.ru/", null)},
                {DIMENSION_REFERER, METRIC_VISIT, dimension(DIMENSION_REFERER).notIn("http://market.yandex.ru/", "http://google.com", null)},

                {DIMENSION_DATE, METRIC_HIT, dimension(DIMENSION_DEVICE_CATEGORY_NAME).equalTo("Планшеты")},
                {DIMENSION_DATE, METRIC_HIT, dimension(DIMENSION_DEVICE_CATEGORY_NAME).equalTo("ПК")},
                {DIMENSION_DATE, METRIC_HIT, dimension(DIMENSION_DEVICE_CATEGORY_NAME).equalTo("ТВ")},
        });
    }
}
