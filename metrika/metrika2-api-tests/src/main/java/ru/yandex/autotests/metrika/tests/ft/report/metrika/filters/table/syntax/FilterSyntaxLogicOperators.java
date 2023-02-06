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
import static ru.yandex.autotests.metrika.filters.Not.not;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by konkov on 12.05.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: логические операторы")
@RunWith(Parameterized.class)
public class FilterSyntaxLogicOperators extends FilterSyntaxBaseTest {
    private final static String DIMENSION_GOAL = "ym:s:goal";
    private final static String DIMENSION_VISITS = "ym:s:lastTrafficSource";
    private final static String METRIC_VISIT = "ym:s:visits";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION_GOAL, METRIC_VISIT,
                        dimension(DIMENSION_GOAL).equalTo(COUNTER.get(Counter.GOAL_ID))
                                .and(dimension(DIMENSION_VISITS).equalTo("organic"))},
                {DIMENSION_GOAL, METRIC_VISIT,
                        dimension(DIMENSION_GOAL).equalTo(COUNTER.get(Counter.GOAL_ID))
                                .or(dimension(DIMENSION_VISITS).equalTo("organic"))},
                {DIMENSION_GOAL, METRIC_VISIT,
                        not(dimension(DIMENSION_GOAL).equalTo(COUNTER.get(Counter.GOAL_ID)))
                                .or(dimension(DIMENSION_VISITS).equalTo("organic"))},
                {DIMENSION_GOAL, METRIC_VISIT,
                        not(dimension(DIMENSION_GOAL).equalTo(COUNTER.get(Counter.GOAL_ID))
                                .or(dimension(DIMENSION_VISITS).equalTo("organic")))},
                {DIMENSION_GOAL, METRIC_VISIT,
                        not(dimension(DIMENSION_GOAL).equalTo(COUNTER.get(Counter.GOAL_ID)))},
                {DIMENSION_GOAL, METRIC_VISIT,
                        not(not(dimension(DIMENSION_GOAL).equalTo(COUNTER.get(Counter.GOAL_ID))))},
                {DIMENSION_GOAL, METRIC_VISIT,
                        not(not(not(dimension(DIMENSION_GOAL).equalTo(COUNTER.get(Counter.GOAL_ID)))))},
        });
    }
}
