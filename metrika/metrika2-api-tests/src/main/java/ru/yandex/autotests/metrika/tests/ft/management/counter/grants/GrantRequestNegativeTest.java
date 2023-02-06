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
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Objects;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.junit.Assume.assumeThat;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.errors.ManagementError.NO_OBJECT_ID;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.createGrantRequestNegativeParam;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.metrika.api.management.client.external.GrantType.VIEW;

/**
 * Created by konkov on 08.12.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({
        Requirements.Story.Management.COUNTERS,
        Requirements.Story.Management.GRANTS
})
@Title("Проверка запросов на доступы (негативные)")
@RunWith(Parameterized.class)
public class GrantRequestNegativeTest {

    private static UserSteps user;
    private static UserSteps userOwner;
    private UserSteps userDecider;

    private static final User OWNER = USER_DELEGATOR;
    private static final User SOME_OTHER_USER = SIMPLE_USER;
    private static final User GRANTED_USER = SIMPLE_USER3;
    private static final User REQUESTOR = SIMPLE_USER2;

    @Parameter(0)
    public AddGrantRequestObjectWrapper grantRequest;

    @Parameter(1)
    public CounterGrantRequestObjectWrapper actualGrantRequest;

    @Parameter(2)
    public User decider;

    @Parameter(3)
    public IExpectedError expectedError;

    private Long counterId;

    @Parameters(name = "Запрос: {0}, как обрабатывается: {1}, кто обрабатывает: {2}, ошибка: {3}")
    public static Collection<Object[]> createParameters() {
        return asList(
                createParam(REQUESTOR, "not-a-login", OWNER, NO_OBJECT_ID),
                createParam(REQUESTOR, SOME_OTHER_USER.get(LOGIN), OWNER, NO_OBJECT_ID),
                createParam(REQUESTOR, REQUESTOR.get(LOGIN), SOME_OTHER_USER, ACCESS_DENIED),
                createParam(REQUESTOR, REQUESTOR.get(LOGIN), GRANTED_USER, ACCESS_DENIED)
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

        //выдать гостевой доступ
        userOwner.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId,
                new GrantE()
                        .withUserLogin(GRANTED_USER.get(LOGIN))
                        .withPerm(VIEW));

        user.onManagementSteps().onGrantRequestsSteps()
                .requestGrantAndExpectSuccess(grantRequest.getClone().withObjectId(Objects.toString(counterId)));
    }

    @Test
    public void list() {
        /* В этом тесте специально используется junit импорт для assumeThat
         Это сделано для того, чтобы тест для первых двух параметров исключался,
         так как там в роли decider выступает owner
         */
        assumeThat("владелец всегда может получить список запросов на доступ", decider, not(equalTo(OWNER)));

        userDecider.onManagementSteps().onGrantRequestsSteps()
                .getGrantRequestsAndExpectError(expectedError, counterId);
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
        userOwner.onManagementSteps().onGrantsSteps().deleteGrantAndExpectSuccess(counterId, GRANTED_USER.get(LOGIN));
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

    private static Object[] createParam(User requestor, String userLogin, User decider, IExpectedError error) {
        return createGrantRequestNegativeParam(OWNER, requestor, userLogin, decider, error);
    }

}
