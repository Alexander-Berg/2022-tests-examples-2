package ru.yandex.autotests.metrika.tests.ft.management.counter.boundary;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.operation.OperationE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.List;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Field.OPERATIONS;
import static ru.yandex.autotests.metrika.errors.ManagementError.OPERATIONS_LIMIT;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getOperation;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getOperations;

/**
 * Created by okunev on 09.09.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Тест заданного ограничения на количество операций в счетчике")
public class CounterMaxOperationsCustomValueTest {

    private static final User USER = SIMPLE_USER;
    private static final Counter COUNTER = Counters.TEST_COUNTER_LIMITS;
    private static final int CUSTOM_MAX_OPERATIONS = 40;

    private static UserSteps user;

    private List<OperationE> addedOperations = new ArrayList<>();

    @BeforeClass
    public static void init() {
        user = new UserSteps().withUser(USER);
    }

    @Before
    public void setup() {
        CounterFull counterInfo = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(COUNTER.get(ID), OPERATIONS);

        int currentOperations = counterInfo.getOperations().size();

        List<OperationE> operations = getOperations(CUSTOM_MAX_OPERATIONS - currentOperations);

        addedOperations = user.onManagementSteps().onOperationsSteps().addOperations(COUNTER.get(ID), operations);
    }

    @Test
    public void createMoreThanMaximumNumberOfOperations() {
        user.onManagementSteps().onOperationsSteps()
                .addOperationAndExpectError(OPERATIONS_LIMIT, COUNTER.get(ID), getOperation());
    }

    @After
    public void teardown() {
        user.onManagementSteps().onOperationsSteps().deleteOperations(COUNTER.get(ID), addedOperations);
    }

}
