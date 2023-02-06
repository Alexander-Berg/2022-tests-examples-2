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
import static ru.yandex.autotests.metrika.filters.Relation.*;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by konkov on 08.05.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: сегментация по измерениям из множеств")
@RunWith(Parameterized.class)
public class FilterSyntaxSetTest extends FilterSyntaxBaseTest {

    private final static String DIMENSION = "ym:s:goal";
    private final static String METRIC = "ym:s:users";

    private final static String DIMENSION_GOAL = "ym:s:goal";
    private final static String DIMENSION_PARAMS = "ym:s:paramsLevel1";
    private final static String DIMENSION_INTEREST = "ym:s:interest";
    private final static String DIMENSION_URL_PARAM = "ym:pv:URLParamName";
    private final static String DIMENSION_REFERER = "ym:s:referer";


    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION, METRIC, exists(dimension(DIMENSION_GOAL).equalTo(COUNTER.get(Counter.GOAL_ID)))},
                {DIMENSION, METRIC, all(dimension(DIMENSION_GOAL).equalTo(COUNTER.get(Counter.GOAL_ID)))},
                {DIMENSION, METRIC, none(dimension(DIMENSION_GOAL).equalTo(COUNTER.get(Counter.GOAL_ID)))},
                {DIMENSION, METRIC, exists(dimension(DIMENSION_PARAMS).equalTo(null))},
                {DIMENSION, METRIC, all(dimension(DIMENSION_PARAMS).equalTo(null))},
                {DIMENSION, METRIC, none(dimension(DIMENSION_PARAMS).equalTo(null))},
                {DIMENSION, METRIC, exists(dimension(DIMENSION_URL_PARAM).equalTo("category"))},
                {DIMENSION, METRIC, all(dimension(DIMENSION_URL_PARAM).equalTo("category"))},
                {DIMENSION, METRIC, none(dimension(DIMENSION_URL_PARAM).equalTo("category"))},

                {DIMENSION, METRIC, exists(dimension(DIMENSION_INTEREST).equalTo("literature"))},
                {DIMENSION, METRIC, exists(dimension(DIMENSION_INTEREST).in("literature"))},
                {DIMENSION, METRIC, exists(dimension(DIMENSION_INTEREST).in("literature", "cinema"))},
                {DIMENSION, METRIC, exists(dimension(DIMENSION_INTEREST).notIn("literature", "cinema"))},

                {DIMENSION, METRIC, all(dimension(DIMENSION_INTEREST).equalTo("literature"))},
                {DIMENSION, METRIC, all(dimension(DIMENSION_INTEREST).in("literature"))},
                {DIMENSION, METRIC, all(dimension(DIMENSION_INTEREST).in("literature", "cinema"))},
                {DIMENSION, METRIC, all(dimension(DIMENSION_INTEREST).notIn("literature", "cinema"))},

                {DIMENSION, METRIC, none(dimension(DIMENSION_INTEREST).equalTo("literature"))},
                {DIMENSION, METRIC, none(dimension(DIMENSION_INTEREST).in("literature"))},
                {DIMENSION, METRIC, none(dimension(DIMENSION_INTEREST).in("literature", "cinema"))},
                {DIMENSION, METRIC, none(dimension(DIMENSION_INTEREST).notIn("literature", "cinema"))},

                {DIMENSION, METRIC, exists(dimension(DIMENSION_REFERER).equalTo("http://yandex.ru/"))},
                {DIMENSION, METRIC, all(dimension(DIMENSION_REFERER).equalTo("http://yandex.ru/"))},
                {DIMENSION, METRIC, none(dimension(DIMENSION_REFERER).equalTo("http://yandex.ru/"))},
        });
    }
}
