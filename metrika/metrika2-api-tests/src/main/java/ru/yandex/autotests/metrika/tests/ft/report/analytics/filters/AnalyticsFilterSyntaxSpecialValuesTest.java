package ru.yandex.autotests.metrika.tests.ft.report.analytics.filters;

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
 * Created by sourx on 27.05.2016.
 */
@Features(Requirements.Feature.ANALYTICS)
@Stories({Requirements.Story.Report.Type.ANALYTICS, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры (google analytics): специальные символы в аргументах операторов")
@RunWith(Parameterized.class)
public class AnalyticsFilterSyntaxSpecialValuesTest extends AnalyticsFilterSyntaxBaseTest {
    private final static String METRIC = "ga:users";
    private final static String DIMENSION = "ga:pagePath";

    @Parameterized.Parameters()
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {DIMENSION, METRIC, dimension(DIMENSION).equalTo("\\")},
                {DIMENSION, METRIC, dimension(DIMENSION).equalTo("'")},
                {DIMENSION, METRIC, dimension(DIMENSION).equalTo("\"")},
                {DIMENSION, METRIC, dimension(DIMENSION).equalTo("\0")},
                {DIMENSION, METRIC, dimension(DIMENSION).equalTo("\b")},
                {DIMENSION, METRIC, dimension(DIMENSION).equalTo("\t")},
                {DIMENSION, METRIC, dimension(DIMENSION).equalTo("\n")},
                {DIMENSION, METRIC, dimension(DIMENSION).equalTo("\f")},
                {DIMENSION, METRIC, dimension(DIMENSION).equalTo("\r")},
                {DIMENSION, METRIC, dimension(DIMENSION).equalTo("\r\n")},
                {DIMENSION, METRIC, dimension(DIMENSION).equalTo("\n\r")},
                {DIMENSION, METRIC, dimension(DIMENSION).equalTo("\uFFFF")},

                {DIMENSION, METRIC, metric(METRIC).equalTo("1")},
                {DIMENSION, METRIC, metric(METRIC).equalTo(1)},
                {DIMENSION, METRIC, metric(METRIC).lessThan(0)},
                {DIMENSION, METRIC, metric(METRIC).greaterThan(0)},
                {DIMENSION, METRIC, metric(METRIC).equalTo(-1)},
                {DIMENSION, METRIC, metric(METRIC).equalTo(2.5)},
                {DIMENSION, METRIC, metric(METRIC).lessThanOrEqualTo(1e10)},
                {DIMENSION, METRIC, metric(METRIC).greaterThanOrEqualTo(1e-10)},
                {DIMENSION, METRIC, metric(METRIC).lessThanOrEqualTo(-1e-10)},
                {DIMENSION, METRIC, metric(METRIC).greaterThanOrEqualTo(-1e10)},
        });
    }
}
