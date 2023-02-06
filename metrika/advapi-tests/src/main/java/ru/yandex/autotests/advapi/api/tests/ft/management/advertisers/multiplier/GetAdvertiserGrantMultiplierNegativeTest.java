package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers.multiplier;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.advapi.Errors.ACCESS_DENIED;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createSimpleAdvertiser;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_A;

@Features(MANAGEMENT)
@Title("Получение множителя для квот, предназначенная для работы с грантами рекламодател (негативный)")
public class GetAdvertiserGrantMultiplierNegativeTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final User NOT_OWNER = SIMPLE_USER_A;

    long advertiserId;

    @Before
    public void setUp() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
    }

    @Test
    public void getAdvertiserGrantMultiplierNegative() {
        UserSteps.withUser(NOT_OWNER).onAdvertisersSteps()
                .getAdvertiserGrantMultiplierAndExpectError(advertiserId, ACCESS_DENIED);
    }

    @After
    public void cleanUp() {
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
