package ru.yandex.autotests.metrika.tests.ft.report.metrika.date;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.function.BiFunction;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;
import static ru.yandex.autotests.metrika.data.parameters.ParametersUtils.*;

@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.Parameter.DATE)
@Title("Период выборки. Проверка валидации")
@RunWith(Parameterized.class)
public class DateNegativeTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();
    private static final Counter COUNTER = CounterConstants.LITE_DATA;

    private static final String METRIC_NAME = "ym:pv:pageviews";

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public BiFunction<String, String, IFormParameters> parameters;

    @Parameterized.Parameter(2)
    public String startDate;

    @Parameterized.Parameter(3)
    public String endDate;

    @Parameterized.Parameter(4)
    public IExpectedError message;

    @Parameterized.Parameters(name = "{0} {2}:{3}:{4}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(TABLE, dateParameters()),
                        of(DRILLDOWN, dateParameters()),
                        of(COMPARISON, segmentAdateParameters()),
                        of(COMPARISON, segmentBdateParameters()),
                        of(COMPARISON_DRILLDOWN, segmentAdateParameters()),
                        of(COMPARISON_DRILLDOWN, segmentBdateParameters()),
                        of(BY_TIME, dateParameters()))
                .vectorValues(
                        DateNegativeTestData.getNegativeDateParameters())
                .build();
    }

    @Test
    public void checkDatesValidationTest() {
        user.onReportSteps().getReportAndExpectError(
                requestType,
                message,
                new CommonReportParameters()
                        .withId(COUNTER)
                        .withMetric(METRIC_NAME),
                dateParameters().apply(startDate, endDate));
    }

}
