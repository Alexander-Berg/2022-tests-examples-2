package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.errors.ReportError;
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
@Title("Фильтры: операторы для измерений (негативные)")
@RunWith(Parameterized.class)
public class FilterSyntaxNegativeDimensionOperatorsTest extends FilterNegativeBaseTest {
    private final static String DIMENSION_GOAL = "ym:s:goal";
    private final static String DIMENSION_VISIT_DURATION = "ym:s:visitDuration";

    private final static String METRIC_VISIT = "ym:s:visits";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).greaterThan(1)},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).lessThan(1)},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).greaterThanOrEqualTo(1)},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).lessThanOrEqualTo(1)},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).matchSubstring("1")},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).notMatchSubstring("1")},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).matchRegEx(".*")},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).notMatchRegEx(".*")},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).matchStar("*")},
                {DIMENSION_GOAL, METRIC_VISIT, dimension(DIMENSION_GOAL).notMatchStar("*")},

                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).matchSubstring("1")},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).notMatchSubstring("1")},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).matchRegEx(".*")},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).notMatchRegEx(".*")},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).matchStar("*")},
                {DIMENSION_VISIT_DURATION, METRIC_VISIT, dimension(DIMENSION_VISIT_DURATION).notMatchStar("*")},
        });
    }

    @Override
    protected IExpectedError getExpectedError() {
        return ReportError.OPERATOR_NOT_SUPPORTED_FOR_DIMENSION;
    }
}
