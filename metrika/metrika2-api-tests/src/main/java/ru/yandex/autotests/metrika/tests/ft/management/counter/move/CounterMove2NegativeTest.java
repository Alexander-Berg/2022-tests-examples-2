package ru.yandex.autotests.metrika.tests.ft.management.counter.move;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.CounterFullObjectWrapper;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.errors.ManagementError.USER_IS_ALREADY_OWNER;
import static ru.yandex.autotests.metrika.errors.ManagementError.WRONG_COUNTER;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;

/**
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка отбирания счетчика, негативнные тесты")
@RunWith(Parameterized.class)
public class CounterMove2NegativeTest {

    private static final User OWNER = USER_DELEGATOR;
    private static UserSteps userOwner = new UserSteps().withUser(OWNER);

    private UserSteps userMover;
    private Long counterId;

    @Parameter()
    public CounterFullObjectWrapper counterWrapper;

    @Parameter(1)
    public User mover;

    @Parameter(2)
    public User recipient;

    @Parameter(3)
    public ManagementError expectedError;

    @Parameter(4)
    public IFormParameters additionParams;

    @Parameters(name = "{0}, {1}, {2}, ошибка: {3}")
    public static Collection<Object[]> createParameters() {
        return of(
                createCounterMoveNegativeParam(getCounterWithBasicParameters(),
                        SIMPLE_USER2, SIMPLE_USER2, WRONG_COUNTER),
                createCounterMoveNegativeParam(getDefaultCounterWithViewPermission(SIMPLE_USER2),
                        SIMPLE_USER2, SIMPLE_USER2, WRONG_COUNTER),
                createCounterMoveNegativeParam(getDefaultCounterWithEditPermission(SIMPLE_USER2),
                        SIMPLE_USER2, SIMPLE_USER2, WRONG_COUNTER),
                createCounterMoveNegativeParam(getDefaultCounterWithPublicStatPermission(),
                        SIMPLE_USER2, SIMPLE_USER2, WRONG_COUNTER),
                createCounterMoveNegativeParam(getCounterWithBasicParameters(),
                        USER_DELEGATE_PERMANENT, SIMPLE_USER2, USER_IS_ALREADY_OWNER, ulogin(OWNER.get(LOGIN))),
                createCounterMoveNegativeParam(getDefaultCounter(), OWNER, OWNER, USER_IS_ALREADY_OWNER)
        );
    }

    @Before
    public void setup() {
        userMover = new UserSteps().withUser(mover);

        counterId = userOwner.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(counterWrapper.get()).getId();
    }

    @Test
    public void negativeMoveTest() {
        userMover.onManagementSteps().onCountersSteps()
                .move2CounterAndExpectError(expectedError, counterId, counterWrapper.get().getSite(), recipient.get(LOGIN), additionParams);
    }

    @After
    public void tearDown() {
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
