package ru.yandex.autotests.metrika.tests.ft.management.operations;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.operation.OperationAttribute;
import ru.yandex.metrika.api.management.client.operation.OperationE;
import ru.yandex.metrika.api.management.client.operation.OperationType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Fields.all;
import static ru.yandex.autotests.metrika.errors.ManagementError.NOT_ALLOWED_SYMBOLS_IN_OPERATION_VALUE;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultOperation;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 19.10.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.OPERATIONS)
@Title("Операция: проверка добавления операции (негативные)")
public class AddOperationNegativeTest {

    private static UserSteps user = new UserSteps();

    private Long counterId;

    @Before
    public void setup() {
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    public void addOperationWithNotAllowedSymbolsInValueTest() {
        user.onManagementSteps().onOperationsSteps().addOperationAndExpectError(
                NOT_ALLOWED_SYMBOLS_IN_OPERATION_VALUE,
                counterId,
                new OperationE().withAction(OperationType.REPLACE_DOMAIN).withAttr(OperationAttribute.URL).withValue("\uD83D\uDCC5")
        );
    }

    @After
    public void teardown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
