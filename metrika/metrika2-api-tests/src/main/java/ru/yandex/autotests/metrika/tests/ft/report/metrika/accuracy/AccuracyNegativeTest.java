package ru.yandex.autotests.metrika.tests.ft.report.metrika.accuracy;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.*;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;

@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Parameter.ACCURACY)
@Title("Негативные тесты на параметр accuracy")
@RunWith(Parameterized.class)
public class AccuracyNegativeTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final String START_DATE = "2014-09-01";
    private static final String END_DATE = "2014-09-02";
    private static final String DIMENSION_NAME = "ym:s:age";
    private static final String METRIC_NAME = "ym:s:visits";

    private static final Counter COUNTER = CounterConstants.NO_DATA;

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameter(2)
    public String accuracy;

    @Parameterized.Parameters(name = "{0} \"{2}\"")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(BY_TIME, new BytimeReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)),
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
                                .withDate2_b(END_DATE))
                )
                .values(of(" ", "1.1", "2", "0", "-1", "Z", "Я", "\u1000", "very long string"))
                .build();
    }

    @Test
    public void accuracyNegativeTest() {
        user.onReportSteps().getReportAndExpectError(requestType, ReportError.WRONG_ACCURACY_FORMAT,
                parameters,
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME)
                        .withAccuracy(accuracy));
    }

}
