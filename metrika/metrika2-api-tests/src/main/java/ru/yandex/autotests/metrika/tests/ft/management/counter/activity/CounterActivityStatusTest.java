package ru.yandex.autotests.metrika.tests.ft.management.counter.activity;

import java.util.List;
import java.util.stream.Collectors;

import org.junit.After;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData;
import ru.yandex.metrika.api.counter.CounterActivityStatus;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.users.Users.MANAGER;
import static ru.yandex.autotests.metrika.data.common.users.Users.METRIKA_TEST_COUNTERS;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка статуса посещаемости счетчика")
public class CounterActivityStatusTest {

    private static final User USER_WITH_COUNTERS = METRIKA_TEST_COUNTERS;
    private static final User MANAGER_USER = MANAGER;
    private static final User USER = SIMPLE_USER;

    private static UserSteps userWithCounters;
    private static UserSteps manager;
    private static UserSteps user;

    private Long counterId;

    @BeforeClass
    public static void init() {
        userWithCounters = new UserSteps().withUser(USER_WITH_COUNTERS);
        manager = new UserSteps().withUser(MANAGER_USER);
        user = new UserSteps().withUser(USER);
    }

    @Test
    @Title("Проверка наличия поля activity_status для списка счетчиков")
    public void checkActivityStatusCounterList() {
        List<CounterBrief> counters = userWithCounters.onManagementSteps().onCountersSteps().getAvailableCountersAndExpectSuccess();
        assumeThat("Список счетчиков не пустой", counters, not(empty()));

        List<CounterActivityStatus> activityStatuses = counters.stream()
                .map(CounterBrief::getActivityStatus)
                .collect(Collectors.toList());
        assertThat("Поле activity_status по умолчанию доступно в списке счётчиков", activityStatuses,
                everyItem(notNullValue()));
    }

    @Test
    @Title("Проверка статуса высокой посещаемости")
    public void checkHighActivityStatus() {
        CounterFull counterInfo = manager.onManagementSteps().onCountersSteps().getCounterInfo(Counters.YANDEX_METRIKA_2_0.get(ID));
        assertThat("Счётчик \"Yandex.Metrika 2.0\" имеет высокую посещаемость", counterInfo.getActivityStatus(),
                equalTo(CounterActivityStatus.HIGH));
    }

    @Test
    @Title("Проверка статуса низкой посещаемости")
    public void checkLowActivityStatus() {
        CounterFull counterInfo = manager.onManagementSteps().onCountersSteps().getCounterInfo(Counters.TEST_COUNTER.get(ID));
        assertThat("Счётчик \"test counter\" имеет низкую посещаемость", counterInfo.getActivityStatus(),
                equalTo(CounterActivityStatus.LOW));
    }

    @Test
    @Title("Проверка статуса низкой посещаемости для нового счетчика")
    public void checkLowActivityStatusNewCounter() {
        CounterFull counter = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(ManagementTestData.getDefaultCounter());
        counterId = counter.getId();
        assertThat("Новый счётчик имеет низкую посещаемость", counter.getActivityStatus(),
                equalTo(CounterActivityStatus.LOW));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
