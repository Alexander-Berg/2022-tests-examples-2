package ru.yandex.autotests.metrika.tests.ft.report.analytics.date;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.analytics.v3.AnalyticsParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.metrika.tests.ft.report.metrika.date.DateNegativeTestData.getNegativeDateGAParameters;
import static ru.yandex.autotests.metrika.tests.ft.report.metrika.date.DateNegativeTestData.toCollectionOfObjectArray;

@Features(Requirements.Feature.ANALYTICS)
@Stories(Requirements.Story.Report.Parameter.DATE)
@Title("Период выборки. Проверка валидации")
@RunWith(Parameterized.class)
public class AnalyticsDateNegativeTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();
    private static final Counter COUNTER = CounterConstants.LITE_DATA;

    @Parameterized.Parameter()
    public String startDate;

    @Parameterized.Parameter(1)
    public String endDate;

    @Parameterized.Parameter(2)
    public IExpectedError message;

    @Parameterized.Parameters(name = "{0}:{1}:{2}")
    public static Collection<Object[]> createParameters() {
        return toCollectionOfObjectArray(getNegativeDateGAParameters());
    }

    @Test
    public void checkDatesValidationTest() {
        user.onReportSteps().getAnalyticsReportAndExpectError(
                message,
                new AnalyticsParameters()
                        .withId(COUNTER.getId()).withMetrics("ga:users")
                        .withStartDate(startDate)
                        .withEndDate(endDate));
    }
}
