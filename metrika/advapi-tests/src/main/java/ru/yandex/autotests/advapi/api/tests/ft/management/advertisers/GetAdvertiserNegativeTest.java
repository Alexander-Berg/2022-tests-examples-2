package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers;

import org.junit.Test;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.advapi.Errors.ACCESS_DENIED;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_A;

@Features(MANAGEMENT)
@Title("Получение рекламодателя (негативные)")
public class GetAdvertiserNegativeTest {

    private static final User GUEST = SIMPLE_USER_A;
    private static final long ADVERTISER_196 = 196L;

    @Title("случайный пользователь не может получить чужого рекламодателя")
    @Test
    public void failToGetAdvertiser() {
        UserSteps.withUser(GUEST).onAdvertisersSteps().getAdvertiserAndExpectError(ADVERTISER_196, ACCESS_DENIED);
    }

    @Title("случайный пользователь не может получить инфомацию о чужом рекламодателе")
    @Test
    public void failToGetAdvertiserInfo() {
        UserSteps.withUser(GUEST).onAdvertisersSteps().getAdvertiserInfoAndExpectError(ADVERTISER_196, ACCESS_DENIED);
    }
}
