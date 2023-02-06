package ru.yandex.autotests.metrika.tests.ft.report.metrika.metrics;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.*;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.errors.CustomError.expect;

@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Parameter.METRICS)
@Title("Проверка включенных фичей на счетчике (негативные)")
@RunWith(Parameterized.class)
public class CounterFeatureNegativeTest {

    private static final UserSteps USER = new UserSteps().withDefaultAccuracy();
    private static final Counter COUNTER = SENDFLOWERS_RU;

    private static final String DIMENSION_NAME = "ym:s:gender";
    private static final String METRIC_NAME = "ym:s:publisherArticleViewsRecircled";

    private static final String START_DATE = "2019-09-24";
    private static final String END_DATE = "2019-09-30";

    private static final Long EXPECTED_ERROR_CODE = 400L;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameter(2)
    public String expectedErrorMessage;

    @Parameterized.Parameters(name = "{0}: {2}")
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
                                .withDate2_b(END_DATE)),
                        of(BY_TIME, new BytimeReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)))
                .vectorValues(
                        of("Wrong parameter: 'metric', value: 'ym:s:publisherArticleViewsRecircled', message: publishers is not enabled for 101024"))
                .build();
    }

    @Test
    public void checkError() {
        USER.onReportSteps().getReportAndExpectError(
                requestType,
                expect(EXPECTED_ERROR_CODE, expectedErrorMessage),
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME),
                parameters);
    }
}
