package ru.yandex.autotests.metrika.tests.ft.management.operations;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.operation.OperationE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Fields.all;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultOperation;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 19.10.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.OPERATIONS)
@Title("Операция: проверка добавления операции")
public class AddOperationTest {

    private static UserSteps user = new UserSteps();

    private Long counterId;
    private OperationE operation;
    private OperationE operationAdded;

    @Before
    public void setup() {
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();

        operation = getDefaultOperation();

        operationAdded = user.onManagementSteps().onOperationsSteps().addOperation(counterId, operation);
    }

    @Test
    public void addOperationTest() {
        assertThat("созданная операция имеет заданные атрибуты", operationAdded, beanEquivalent(operation));
    }

    @Test
    public void addOperationListTest() {
        List<OperationE> operations = user.onManagementSteps().onOperationsSteps().getOperations(counterId);

        assertThat("созданная операция присутствует в списке операций", operations,
                hasItem(beanEquivalent(operation)));
    }

    @Test
    public void addOperationInfoTest() {
        OperationE operationInfo = user.onManagementSteps()
                .onOperationsSteps().getOperation(counterId, operationAdded.getId());

        assertThat("операция имеет заданные атрибуты", operationInfo, beanEquivalent(operation));
    }

    @Test
    public void addOperationCounterTest() {
        CounterFull counter = user.onManagementSteps().onCountersSteps().getCounterInfo(counterId, all());

        assertThat("операция присутствует в списке операций счетчика", counter.getOperations(),
                hasItem(beanEquivalent(operation)));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
