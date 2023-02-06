package ru.yandex.autotests.metrika.tests.ft.report.metrika.pagination;

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
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.limit;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.offset;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;

@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Parameter.LIMIT,
        Requirements.Story.Report.Parameter.OFFSET})
@Title("Получение отчета по частям граничные тесты")
@RunWith(Parameterized.class)
public class PaginationBoundaryTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = CounterConstants.LITE_DATA;

    private static final String START_DATE = "2014-11-26";
    private static final String END_DATE = "2014-11-26";

    private static final String METRIC_NAME = "ym:s:visits";
    private static final String DIMENSION_NAME = "ym:s:browser";

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameter(2)
    public Long limit;

    @Parameterized.Parameter(3)
    public Long offset;

    @Parameterized.Parameters(name = "{0} limit={2} offset={3}")
    public static Collection createParameters() {
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
                        asList(null, null),
                        asList(0L, null),
                        asList(null, 1L),
                        asList(0L, 1L),
                        asList(1L, 1L),
                        asList(1L, 2L),
                        asList(10000L, null))
                .build();
    }

    @Test
    public void paginationBoundaryTest() {
        user.onReportSteps().getReportAndExpectSuccess(requestType,
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withSort(sort().by(METRIC_NAME).descending().build()),
                parameters,
                limit(limit),
                offset(offset));
    }
}
