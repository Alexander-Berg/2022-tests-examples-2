package ru.yandex.autotests.metrika.tests.ft.management.counter.grants;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.errors.ManagementError.GRANTS_QUOTA_EXCEEDING;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getGrant;

/**
 * Created by debychkov on 04.07.17.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка квот на добавление гостевых доступов")
public class GrantQuotasTest {
    private static final User OTHER1 = Users.SIMPLE_USER2;

    private UserSteps user = new UserSteps().withUser(Users.SIMPLE_USER);
    private UserSteps manager = new UserSteps().withUser(Users.MANAGER);
    private UserSteps superUser = new UserSteps().withUser(Users.SUPER_USER);
    private CounterFull counter;
    private CounterFull counterOfManager;
    private CounterFull counterOfSuperUser;

    @Before
    public void setup() {
        counter = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
        counterOfManager = manager.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
        counterOfSuperUser = superUser.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter());
    }

    @Test
    @Title("Проверка квот на добавление гостевых доступов, от имени обычного юзера")
    public void check() {
        long counterId = counter.getId();

        // quota = 3, on testing
        for (int i = 0; i < 3; ++i) {
            user.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId, getGrant(OTHER1));
            user.onManagementSteps().onGrantsSteps()
                    .deleteGrantAndExpectSuccess(counterId, getGrant(OTHER1).getUserLogin());
        }

        user.onManagementSteps().onGrantsSteps().setGrantAndExpectError(GRANTS_QUOTA_EXCEEDING, counterId, getGrant(OTHER1));
    }

    @Test
    @Title("Проверка квот на добавление гостевых доступов, от имени менеджера")
    public void checkForManager() {
        long counterId = counterOfManager.getId();

        // unlimited quota for manager, on testing
        for (int i = 0; i < 10; ++i) {
            manager.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId, getGrant(OTHER1));
            manager.onManagementSteps().onGrantsSteps()
                    .deleteGrantAndExpectSuccess(counterId, getGrant(OTHER1).getUserLogin());
        }
    }
    @Test
    @Title("Проверка квот на добавление гостевых доступов, от имени супер юзера")
    public void checkForSuperUser() {
        long counterId = counterOfSuperUser.getId();

        // unlimited quota for super user, on testing
        for (int i = 0; i < 10; ++i) {
            System.out.println("i = " + i);
            superUser.onManagementSteps().onGrantsSteps().setGrantAndExpectSuccess(counterId, getGrant(OTHER1));
            superUser.onManagementSteps().onGrantsSteps()
                    .deleteGrantAndExpectSuccess(counterId, getGrant(OTHER1).getUserLogin());
        }
    }

    @After
    public void tearDown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counter.getId());
        manager.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterOfManager.getId());
        superUser.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterOfSuperUser.getId());
    }
}
