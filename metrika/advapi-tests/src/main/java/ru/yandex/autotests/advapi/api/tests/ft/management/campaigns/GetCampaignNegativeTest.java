package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.junit.Test;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.advapi.Errors.ACCESS_DENIED;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_A;

@Features(MANAGEMENT)
@Title("Получения кампании (негативные)")
public class GetCampaignNegativeTest {

    private static final UserSteps GUEST = UserSteps.withUser(SIMPLE_USER_A);
    private static final long ADVERTISER_ID = 196;
    private static final long CAMPAIGN_ID = 256;

    @Test
    @Title("Случайный пользователь не может получить доступ не к своей кампании")
    public void getCampaignsByAdvertiser() {
        GUEST.onCampaignsSteps().getCampaignAndExpectError(ADVERTISER_ID, CAMPAIGN_ID, ACCESS_DENIED);
    }
}
