package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.hamcrest.Matchers;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterStatus;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_WITH_EMPTY_TOKEN;
import static ru.yandex.autotests.metrika.errors.ManagementError.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 16.06.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчики: проверка авторизациии")
@Issue("METR-11534")
public class AuthorizationTest {

    private static final User OWNER = SIMPLE_USER;
    private static final User USER = Users.SIMPLE_USER2;

    private static UserSteps userOwner;
    private static UserSteps user;

    private Long counterId;
    private boolean shouldDelete;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withUser(USER);
        userOwner = new UserSteps().withUser(OWNER);
    }

    @Before
    public void setup() {
        counterId = userOwner.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
        shouldDelete = true;
    }

    @Test
    public void noAccessToCounterTest() {
        user.onManagementSteps().onCountersSteps()
                .getCounterInfoAndExpectError(ACCESS_DENIED, counterId);
    }

    @Test
    public void incorrectCounterIdTest() {
        user.onManagementSteps().onCountersSteps()
                .getCounterInfoAndExpectError(ACCESS_DENIED, -1L);
    }

    @Test
    public void noCounterIdTest() {
        userOwner.onManagementSteps().onCountersSteps()
                .deleteCounterAndExpectSuccess(counterId);
        shouldDelete = false;

        user.onManagementSteps().onCountersSteps()
                .getCounterInfoAndExpectError(ACCESS_DENIED, counterId);
    }

    @Test
    public void noCounterIdOwnerTest() {
        userOwner.onManagementSteps().onCountersSteps()
                .deleteCounterAndExpectSuccess(counterId);
        shouldDelete = false;

        CounterFull deletedCounter = userOwner.onManagementSteps().onCountersSteps()
                        .getCounterInfo(counterId);
        assertThat("счетчик удален", deletedCounter.getStatus(),
                equalTo(CounterStatus.DELETED));

    }

    @Test
    public void noPublicStatTest() {
        user.withUser(USER_WITH_EMPTY_TOKEN)
                .onManagementSteps().onCountersSteps()
                .getCounterInfoAndExpectError(UNAUTHORIZED, counterId);
    }

    @After
    public void tearDown() {
        if (shouldDelete) {
            userOwner.onManagementSteps().onCountersSteps()
                    .deleteCounterAndExpectSuccess(counterId);
        }
    }
}
