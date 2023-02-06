package ru.yandex.autotests.metrika.tests.ft.management.counter.grants;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.AddGrantRequestObjectWrapper;
import ru.yandex.autotests.metrika.beans.schemes.CounterGrantRequestObjectWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterGrantRequest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.Objects;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.hasItem;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER2;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATOR;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.createGrantRequestNegativeParam;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sourx on 20/06/16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.COUNTERS,
        Requirements.Story.Management.GRANTS
})
@Title("Проверка запросов на доступы (доступ для менеджеров)")
@RunWith(Parameterized.class)
public class GrantRequestSpecialTest {
    private static UserSteps user;
    private static UserSteps userOwner;
    private UserSteps userDecider;

    private static final User OWNER = USER_DELEGATOR;
    private static final User REQUESTOR = SIMPLE_USER2;
    private static final User MANAGER = Users.MANAGER;
    private static final User MANAGER_DIRECT = Users.MANAGER_DIRECT;

    @Parameter(0)
    public AddGrantRequestObjectWrapper grantRequest;

    @Parameter(1)
    public CounterGrantRequestObjectWrapper actualGrantRequest;

    @Parameter(2)
    public User decider;

    @Parameter(3)
    public IExpectedError expectedError;

    private Long counterId;

    @Parameters(name = "Запрос: {0}, как обрабатывается: {1}, кто обрабатывает: {2}")
    public static Collection<Object[]> createParameters() {
        return asList(
                createParam(REQUESTOR, REQUESTOR.get(LOGIN), MANAGER, ACCESS_DENIED),
                createParam(REQUESTOR, REQUESTOR.get(LOGIN), MANAGER_DIRECT, ACCESS_DENIED)
        );
    }

    @BeforeClass
    public static void init() {
        user = new UserSteps();
        userOwner = new UserSteps().withUser(OWNER);
    }

    @Before
    public void setup() {
        userDecider = new UserSteps().withUser(decider);

        counterId = userOwner.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();

        user.onManagementSteps().onGrantRequestsSteps()
                .requestGrantAndExpectSuccess(grantRequest.getClone().withObjectId(Objects.toString(counterId)));
    }

    @Test
    public void list() {
        List<CounterGrantRequest> grantRequests = userDecider.onManagementSteps().onGrantRequestsSteps()
                .getGrantRequestsAndExpectSuccess(counterId);

        assertThat("запрос на доступ присутствует в списке", grantRequests,
                hasItem(beanEquivalent(actualGrantRequest.get())));
    }

    @Test
    public void accept() {
        userDecider.onManagementSteps().onGrantRequestsSteps()
                .acceptGrantRequestAndExpectError(expectedError, counterId, actualGrantRequest.get());
    }

    @Test
    public void reject() {
        userDecider.onManagementSteps().onGrantRequestsSteps()
                .rejectGrantRequestAndExpectError(expectedError, counterId, actualGrantRequest.get());
    }

    @After
    public void teardown() {
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

    private static Object[] createParam(User requestor, String userLogin, User decider, IExpectedError error) {
        return createGrantRequestNegativeParam(OWNER, requestor, userLogin, decider, error);
    }
}
