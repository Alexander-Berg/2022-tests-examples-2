package ru.yandex.autotests.metrika.tests.ft.management.logsapi;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.logs.LogRequest;
import ru.yandex.metrika.api.management.client.external.logs.LogRequestSource;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.STAT_MTRS;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.tests.ft.management.logsapi.LogsApiTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.LOGS_API})
@Title("Создание загрузки Logs API")
@RunWith(Parameterized.class)
public class LogsApiCreateTest {

    private static final User OWNER = METRIKA_TEST_COUNTERS;
    private static final User GUEST_VIEW = SIMPLE_USER;
    private static final User GUEST_EDIT = SIMPLE_USER2;
    private static final User DELEGATE = USER_DELEGATOR2;

    private static final Long COUNTER_ID = STAT_MTRS.getId();

    protected static final UserSteps userTest = new UserSteps().withDefaultAccuracy();

    private static UserSteps user;

    private static Long logRequestId;

    @Parameterized.Parameter(0)
    public String title;

    @Parameterized.Parameter(1)
    public User currentUser;

    @Parameterized.Parameter(2)
    public String date1;

    @Parameterized.Parameter(3)
    public String date2;

    @Parameterized.Parameter(4)
    public LogRequestSource source;

    @Parameterized.Parameter(5)
    public String fields;

    @Parameterized.Parameters(name = "Пользователь: {0}, за период с {2} по {3}, {4}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of("владелец", OWNER),
                        of("гостевой доступ на редактирование", GUEST_EDIT),
                        of("гостевой доступ на чтение", GUEST_VIEW),
                        of("представитель владельца", DELEGATE),
                        of("суперпользователь", SUPER_USER),
                        of("менеджер", MANAGER),
                        of("менеджер-директ", MANAGER_DIRECT),
                        of("саппорт", SUPPORT))
                .vectorValues(
                        of("2020-09-21","2021-01-21", LogRequestSource.VISITS, VISITS_FIELDS),
                        of("2020-09-21","2021-01-21", LogRequestSource.VISITS, VISITS_PARSED_PARAMS),
                        of("2020-09-21","2021-01-21", LogRequestSource.HITS, HITS_FIELDS)
                )
                .build();
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy().withUser(currentUser);

        logRequestId = user.onManagementSteps().onLogsApiSteps()
                .createLogRequest(COUNTER_ID, date1, date2, source, fields).getRequestId();
    }

    @Test
    public void checkLogrequestId() {
        user.onManagementSteps().onLogsApiSteps().getLogRequest(COUNTER_ID, logRequestId);
    }

    @Test
    public void checkLogrequests() {
        List<LogRequest> logRequests = user.onManagementSteps().onLogsApiSteps().getLogRequests(COUNTER_ID);
        assertThat("загрузка есть в списке загрузок",
                logRequests.stream().map(LogRequest::getRequestId).collect(toList()), hasItem(equalTo(logRequestId)));
    }

    @After
    public void after() {
        userTest.onManagementSteps().onLogsApiSteps().cancel(COUNTER_ID, logRequestId);
    }
}
