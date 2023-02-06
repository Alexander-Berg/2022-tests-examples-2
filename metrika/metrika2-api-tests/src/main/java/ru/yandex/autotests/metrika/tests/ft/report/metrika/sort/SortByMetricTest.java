package ru.yandex.autotests.metrika.tests.ft.report.metrika.sort;

import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.*;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.reportwrappers.Report;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.StringUtils.EMPTY;
import static org.apache.commons.lang3.StringUtils.isEmpty;
import static ru.yandex.autotests.irt.testutils.matchers.OrderMatcher.isAscendingOrdered;
import static ru.yandex.autotests.irt.testutils.matchers.OrderMatcher.isDescendingOrdered;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.matchers.SortMatcher.isSortEqualTo;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 04.08.2016.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Parameter.SORT})
@Title("Сортировка по метрике")
@RunWith(Parameterized.class)
public class SortByMetricTest {
    protected static UserSteps user;
    protected static final Counter COUNTER = CounterConstants.LITE_DATA;

    protected static final String METRIC_NAME = "ym:s:visits";
    protected static final String DIMENSION_NAME = "ym:s:referalSource";

    protected static final String START_DATE = "2014-11-26";
    protected static final String END_DATE = "2014-11-26";

    private Report result;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameter(2)
    public String sort;

    @Parameterized.Parameter(3)
    public Matcher matcher;

    @Parameterized.Parameters(name = "{0}, {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(TABLE, new TableReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)),
                        of(DRILLDOWN, new DrillDownReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)),
                        of(COMPARISON, new ComparisonReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE)),
                        of(COMPARISON_DRILLDOWN, new ComparisonDrilldownReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE)))
                .vectorValues(
                        of(sort().by(METRIC_NAME).build(), isAscendingOrdered()),
                        of(sort().by(METRIC_NAME).descending().build(), isDescendingOrdered()),
                        of(EMPTY, isDescendingOrdered()))
                .build();
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        result = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                parameters,
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withSort(sort));
    }

    @Test
    public void checkSortInQuery() {
        assertThat("результат содержит заданную сортировку",
                result.getSort(),
                isSortEqualTo(getExpectedSort()));
    }

    @Test
    public void checkMetricSorted() {
        List<Double> metricValues = result.getMetric(METRIC_NAME).stream()
                .map(l -> l.get(0))
                .collect(toList());

        assertThat(String.format("значения метрики %s - %s", METRIC_NAME, matcher),
                metricValues, matcher);
    }

    private String getExpectedSort() {
        return isEmpty(sort)
                ? String.format("-%s", METRIC_NAME)
                : sort;
    }
}
