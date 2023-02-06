package ru.yandex.autotests.metrika.tests.ft.report.analytics.filters;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.errors.AnalyticsReportError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.filters.Term.metric;

/**
 * Created by sourx on 27.05.2016.
 */
@Features({Requirements.Feature.ANALYTICS})
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры (google analytics): специальные символы в аргументах операторов (негативные)")
@RunWith(Parameterized.class)
public class AnalyticsFilterSyntaxSpecialValuesNegativeTest extends AnalyticsFilterSyntaxNegativeBaseTest {
    private final static String METRIC = "ga:users";
    private final static String DIMENSION = "ga:pagePath";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION, METRIC, metric(METRIC).equalTo("\\")},
                {DIMENSION, METRIC, metric(METRIC).equalTo("'")},
                {DIMENSION, METRIC, metric(METRIC).equalTo("\"")},
                {DIMENSION, METRIC, metric(METRIC).equalTo("\0")},
                {DIMENSION, METRIC, metric(METRIC).equalTo("\b")},
                {DIMENSION, METRIC, metric(METRIC).equalTo("\t")},
                {DIMENSION, METRIC, metric(METRIC).equalTo("\n")},
                {DIMENSION, METRIC, metric(METRIC).equalTo("\f")},
                {DIMENSION, METRIC, metric(METRIC).equalTo("\r")},
                {DIMENSION, METRIC, metric(METRIC).equalTo("\r\n")},
                {DIMENSION, METRIC, metric(METRIC).equalTo("\n\r")},
                {DIMENSION, METRIC, metric(METRIC).equalTo("\uFFFF")}
        });
    }

    @Override
    protected IExpectedError getExpectedError() {
        return AnalyticsReportError.VALUE_NOT_SUPPORTED_FOR_METRIC;
    }
}
