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
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by konkov on 02.07.2015.
 */
@Features({Requirements.Feature.REPORT})
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: специальные символы в аргументах операторов (негативные)")
@RunWith(Parameterized.class)
public class FilterSyntaxSpecialValuesNegativeTest extends FilterNegativeBaseTest {

    private final static String DIMENSION_VISIT_PARAMS = "ym:s:paramsLevel1";
    private final static String METRIC_SUM_PARAMS = "ym:s:sumParams";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("\\")},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("'")},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("\"")},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("\0")},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("\b")},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("\t")},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("\n")},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("\f")},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("\r")},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("\r\n")},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("\n\r")},
                {DIMENSION_VISIT_PARAMS, METRIC_SUM_PARAMS, metric(METRIC_SUM_PARAMS).equalTo("\uFFFF")},
        });
    }

    @Override
    protected IExpectedError getExpectedError() {
        return ReportError.UNSUPPORTED_METRIC_VALUE;
    }
}
