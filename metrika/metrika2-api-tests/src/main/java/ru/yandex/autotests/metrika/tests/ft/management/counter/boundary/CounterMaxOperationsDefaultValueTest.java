package ru.yandex.autotests.metrika.tests.ft.management.counter.boundary;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.errors.ManagementError.OPERATIONS_LIMIT;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;

/**
 * Created by okunev on 09.09.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Тест ограничения на количество операций в счетчике по умолчанию")
public class CounterMaxOperationsDefaultValueTest {


    private static final User USER = SIMPLE_USER;
    private static final int DEFAULT_MAX_OPERATIONS = 30;

    private static UserSteps user;
    private Long counterId;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withUser(USER);
    }

    @Before
    public void setup() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();

        user.onManagementSteps().onOperationsSteps().addOperations(counterId, getOperations(DEFAULT_MAX_OPERATIONS));
    }

    @Test
    public void createMoreThanMaximumNumberOfOperations() {
        user.onManagementSteps().onOperationsSteps()
                .addOperationAndExpectError(OPERATIONS_LIMIT, counterId, getOperation());
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

}
