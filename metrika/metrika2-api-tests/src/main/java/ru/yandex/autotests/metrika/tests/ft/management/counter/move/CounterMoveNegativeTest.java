package ru.yandex.autotests.metrika.tests.ft.management.counter.move;

import java.util.Collection;

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
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER2;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATE_PERMANENT;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATOR;
import static ru.yandex.autotests.metrika.data.common.users.Users.YA_METRIKA;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.errors.ManagementError.COUNTERS_MAX_COUNT_EXCEEDED;
import static ru.yandex.autotests.metrika.errors.ManagementError.UNABLE_MOVE_TO_YANDEX_WITH_DIRECT_ALLOW_USE_GOALS_WITHOUT_ACCESS;
import static ru.yandex.autotests.metrika.errors.ManagementError.USER_IS_ALREADY_OWNER;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.createCounterMoveNegativeParam;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.createCounterMoveNegativeParamWithCounterLimitExceeded;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterWithBasicParameters;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterWithDirectAllowUseGoalsWithoutAccess;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithEditPermission;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithPublicStatPermission;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithViewPermission;

/**
 * Created by konkov on 08.06.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка переноса счетчика, негативнные тесты")
@Issue("METR-16688")
@RunWith(Parameterized.class)
public class CounterMoveNegativeTest {
    private static final User OWNER = USER_DELEGATOR;
    private static UserSteps userOwner = new UserSteps().withUser(OWNER);

    private UserSteps userMover;
    private Long counterId;

    @Parameter(0)
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
                        SIMPLE_USER2, SIMPLE_USER2, ACCESS_DENIED),
                createCounterMoveNegativeParam(getDefaultCounterWithViewPermission(SIMPLE_USER2),
                        SIMPLE_USER2, SIMPLE_USER2, ACCESS_DENIED),
                createCounterMoveNegativeParam(getDefaultCounterWithEditPermission(SIMPLE_USER2),
                        SIMPLE_USER2, SIMPLE_USER2, ACCESS_DENIED),
                createCounterMoveNegativeParam(getDefaultCounterWithPublicStatPermission(),
                        SIMPLE_USER2, SIMPLE_USER2, ACCESS_DENIED),
                createCounterMoveNegativeParam(getCounterWithBasicParameters(),
                        USER_DELEGATE_PERMANENT, SIMPLE_USER2, ACCESS_DENIED, ulogin(OWNER.get(LOGIN))),
                createCounterMoveNegativeParam(getDefaultCounter(), OWNER, OWNER, USER_IS_ALREADY_OWNER),
                createCounterMoveNegativeParamWithCounterLimitExceeded(COUNTERS_MAX_COUNT_EXCEEDED),
                createCounterMoveNegativeParam(getCounterWithDirectAllowUseGoalsWithoutAccess(),
                        OWNER, YA_METRIKA, UNABLE_MOVE_TO_YANDEX_WITH_DIRECT_ALLOW_USE_GOALS_WITHOUT_ACCESS)
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
                .moveCounterAndExpectError(expectedError, counterId, recipient.get(LOGIN), additionParams);
    }

    @After
    public void tearDown() {
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
