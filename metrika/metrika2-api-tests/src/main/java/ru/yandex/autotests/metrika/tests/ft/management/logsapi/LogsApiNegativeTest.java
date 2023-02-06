package ru.yandex.autotests.metrika.tests.ft.management.logsapi;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.logs.LogRequestSource;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.Collection;

import static ru.yandex.autotests.metrika.data.common.users.Users.METRIKA_TEST_COUNTERS;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPPORT;
import static ru.yandex.autotests.metrika.errors.LogsApiError.*;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.logsapi.LogsApiTestData.*;
import static ru.yandex.metrika.api.management.client.external.logs.LogRequestSource.HITS;
import static ru.yandex.metrika.api.management.client.external.logs.LogRequestSource.VISITS;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LOGS_API)
@RunWith(Parameterized.class)
@Title("Logs API: получение заказов логов, негативные")
public class LogsApiNegativeTest {

    private static UserSteps user;

    private static Long STAT_MTRS = Counters.STAT_MTRS.getId();
    private static Long SENDFLOWERS = Counters.SENDFLOWERS_RU.getId();

    private static String today = LocalDate.now().toString();

    @Parameterized.Parameter(0)
    public Long counterId;

    @Parameterized.Parameter(1)
    public String date1;

    @Parameterized.Parameter(2)
    public String date2;

    @Parameterized.Parameter(3)
    public LogRequestSource source;

    @Parameterized.Parameter(4)
    public String fields;

    @Parameterized.Parameter(5)
    public IExpectedError error;

    @Parameterized.Parameter(6)
    public User currentUser;

    @Parameterized.Parameters(name = "Счетчик: {0}, период с {1} по {2}, {3}, ошибка {5}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(new Object[][]{
                {STAT_MTRS, today, today, VISITS, VISITS_TIME_AND_PARAMS, INVALID_DATE2, METRIKA_TEST_COUNTERS},
                {STAT_MTRS, "2019-10-3","2019-10-2", VISITS, VISITS_FIELDS, WRONG_PERIOD, METRIKA_TEST_COUNTERS},
                {STAT_MTRS, "2019-10-3","2019-10-2", HITS, HITS_FIELDS, WRONG_PERIOD, METRIKA_TEST_COUNTERS},
                {SENDFLOWERS, "2020-09-21","2021-01-21", VISITS, VISITS_FIELDS, ACCESS_DENIED, METRIKA_TEST_COUNTERS},
                {SENDFLOWERS, "2020-09-21","2021-01-21", VISITS, VISITS_PARSED_PARAMS, ACCESS_DENIED, METRIKA_TEST_COUNTERS},
                {SENDFLOWERS,"2020-09-21","2021-01-21", HITS, HITS_FIELDS, ACCESS_DENIED, METRIKA_TEST_COUNTERS},
                {SENDFLOWERS, "2010-01-01", "2021-01-01", HITS, HITS_FIELDS, TOO_BIG_DATE_INTERVAL, SUPPORT},
                {SENDFLOWERS, "2021-01-01", "2021-01-01", HITS, HITS_FIELDS+","+HITS_FIELDS+","+HITS_FIELDS, TOO_LONG_FIELDS, SUPPORT},
        });
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy().withUser(currentUser);
    }

    @Test
    public void postLogRequestAndExpectError() {
        user.onManagementSteps().onLogsApiSteps()
                .createLogRequestAndExpectError(error, counterId, date1, date2, source, fields);
    }
}
