package ru.yandex.autotests.metrika.tests.ft.management.counter.quota;

import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_COUNTER_NO_QUOTA;
import static ru.yandex.autotests.metrika.errors.ManagementError.COUNTER_QUOTA_EXCEEDING;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка корректности ошибки при превышении квоты по счетчику")
public class CounterQuotaExceedTest {

    private UserSteps user = new UserSteps().withUser(Users.METRIKA_TEST_COUNTERS);
    private static final String METRIC_NAME = "ym:s:visits";
    private static final String DIMENSION_NAME = "ym:s:interest";

    @Test
    public void getReport() {
        user.onReportSteps().getReportAndExpectError(RequestTypes.TABLE, COUNTER_QUOTA_EXCEEDING,
                new CommonReportParameters()
                        .withId(TEST_COUNTER_NO_QUOTA)
                        .withDimension(DIMENSION_NAME)
                        .withMetric(METRIC_NAME));
    }
}
