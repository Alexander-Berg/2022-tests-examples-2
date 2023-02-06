package ru.yandex.autotests.metrika.tests.ft.report.metrika.pagination;

import com.google.common.collect.ImmutableList;
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
import ru.yandex.autotests.metrika.reportwrappers.Report;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.limit;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.offset;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Parameter.LIMIT,
        Requirements.Story.Report.Parameter.OFFSET})
@Title("Получение отчета по частям")
@RunWith(Parameterized.class)
public class PaginationTest {

    private static UserSteps user;

    private static final Long FIRST_INDEX = 10L;
    private static final Long MID_INDEX = 15L;
    private static final Long LAST_INDEX = 20L;

    private static final Counter COUNTER = CounterConstants.LITE_DATA;

    private static final String START_DATE = "2014-11-26";
    private static final String END_DATE = "2014-11-26";

    private static final String METRIC_NAME = "ym:s:visits";
    private static final String DIMENSION_NAME = "ym:s:browser";

    private Report firstPart;
    private Report secondPart;
    private Report bothParts;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(toArray(TABLE, new TableReportParameters()
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)))
                .add(toArray(DRILLDOWN, new DrillDownReportParameters()
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)))
                .add(toArray(COMPARISON, new ComparisonReportParameters()
                        .withDate1_a(START_DATE)
                        .withDate2_a(END_DATE)
                        .withDate1_b(START_DATE)
                        .withDate2_b(END_DATE)))
                .add(toArray(COMPARISON_DRILLDOWN, new ComparisonDrilldownReportParameters()
                        .withDate1_a(START_DATE)
                        .withDate2_a(END_DATE)
                        .withDate1_b(START_DATE)
                        .withDate2_b(END_DATE)))
                .build();
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        firstPart = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withSort(sort().by(METRIC_NAME).descending().build()),
                parameters,
                limit(MID_INDEX - FIRST_INDEX),
                offset(FIRST_INDEX));

        assumeThat("отчет содержит данные", firstPart.getTotalRows(), greaterThan(0L));

        secondPart = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withSort(sort().by(METRIC_NAME).descending().build()),
                parameters,
                limit(LAST_INDEX - MID_INDEX),
                offset(MID_INDEX));

        assumeThat("отчет содержит данные", secondPart.getTotalRows(), greaterThan(0L));

        bothParts = user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withSort(sort().by(METRIC_NAME).descending().build()),
                parameters,
                limit(LAST_INDEX - FIRST_INDEX),
                offset(FIRST_INDEX));

        assumeThat("отчет содержит данные", bothParts.getTotalRows(), greaterThan(0L));
    }

    @Test
    public void paginationMetricsTest() {

        List<List<List<Double>>> combinedMetricsPart = new ArrayList<>();
        combinedMetricsPart.addAll(firstPart.getMetrics());
        combinedMetricsPart.addAll(secondPart.getMetrics());

        List<List<List<Double>>> bothMetricsPart = bothParts.getMetrics();

        assertThat("значения метрик, полученные по частям, совпадают с полученными одним запросом",
                combinedMetricsPart, equalTo(bothMetricsPart));
    }

    @Test
    public void paginationDimensionsTest() {
        List<List<String>> combinedDimensionsPart = new ArrayList<>();
        combinedDimensionsPart.addAll(firstPart.getDimensions());
        combinedDimensionsPart.addAll(secondPart.getDimensions());

        List<List<String>> bothDimensionsPart = bothParts.getDimensions();

        assertThat("значения измерений, полученные по частям, совпадают с полученными одним запросом",
                combinedDimensionsPart, equalTo(bothDimensionsPart));
    }
}
