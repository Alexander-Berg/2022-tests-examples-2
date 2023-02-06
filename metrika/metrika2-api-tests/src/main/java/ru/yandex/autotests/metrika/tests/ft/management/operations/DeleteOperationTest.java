package ru.yandex.autotests.metrika.tests.ft.management.operations;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ReportError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.operation.OperationE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
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
@Title("Операция: проверка удаления операции")
public class DeleteOperationTest {

    private static UserSteps user = new UserSteps();

    private Long counterId;
    private OperationE operation;
    private Long operationId;

    @Before
    public void setup() {
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();

        operation = getDefaultOperation();

        operationId = user.onManagementSteps().onOperationsSteps().addOperation(counterId, operation).getId();

        user.onManagementSteps().onOperationsSteps().deleteOperation(counterId, operationId);
    }

    @Test
    public void deleteOperationTest() {
        user.onManagementSteps().onOperationsSteps().getOperationAndExpectError(
                ReportError.NO_OBJECT_ID,
                counterId, operationId);
    }

    @Test
    public void deleteOperationListTest() {
        List<OperationE> operations = user.onManagementSteps().onOperationsSteps().getOperations(counterId);

        assertThat("удаленная операция отсутствует в списке операций", operations,
                not(hasItem(beanEquivalent(operation))));
    }

    @Test
    public void deleteOperationCounterTest() {
        CounterFull counter = user.onManagementSteps().onCountersSteps().getCounterInfo(counterId, all());

        assertThat("удаленная операция отсутствует в списке операций счетчика", counter.getOperations(),
                not(hasItem(beanEquivalent(operation))));
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
