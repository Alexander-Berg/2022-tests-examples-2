package ru.yandex.autotests.metrika.tests.ft.management.operations;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.actions.EditAction;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.operation.OperationAttribute;
import ru.yandex.metrika.api.management.client.operation.OperationE;
import ru.yandex.metrika.api.management.client.operation.OperationStatus;
import ru.yandex.metrika.api.management.client.operation.OperationType;
import ru.yandex.metrika.util.wrappers.OperationWrapper;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 19.10.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.OPERATIONS)
@Title("Операция: проверка изменения операции")
@RunWith(Parameterized.class)
public class EditOperationTest {

    private static UserSteps user = new UserSteps();

    private static Long counterId;
    private Long operationId;
    private OperationE changedOperaton;
    private OperationE editedOperation;

    @Parameterized.Parameter(0)
    public OperationWrapper operationWrapper;

    @Parameterized.Parameter(1)
    public EditAction<OperationE> editAction;

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> createParameters() {
        return asList(
                createEditParam(getDefaultOperation(), getChangeAction(OperationType.MERGE_HTTPS_AND_HTTP)),
                createEditParam(getDefaultOperation(), getChangeAttr(OperationAttribute.REFERER)),
                createEditParam(getDefaultOperation(), getChangeValue("some value")),
                createEditParam(getDefaultOperation(), getChangeStatus(OperationStatus.DISABLED))
        );
    }

    @BeforeClass
    public static void init() {
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Before
    public void setup() {
        operationId = user.onManagementSteps().onOperationsSteps()
                .addOperation(counterId, operationWrapper.getOperation()).getId();

        changedOperaton = editAction.edit(operationWrapper.getOperation());
        editedOperation = user.onManagementSteps().onOperationsSteps()
                .editOperation(counterId, operationId, changedOperaton);
    }

    @Test
    public void editOperationTest() {
        assertThat("отредактированная операция должна быть эквивалентна измененной", editedOperation,
                beanEquivalent(changedOperaton));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
    }
}
