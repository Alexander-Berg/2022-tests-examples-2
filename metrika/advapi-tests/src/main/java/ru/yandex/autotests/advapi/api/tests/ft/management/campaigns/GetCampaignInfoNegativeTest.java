package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.junit.Test;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.advapi.Errors.ACCESS_DENIED;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;

@Features(MANAGEMENT)
@Title("Получение информации о кампании (негативные)")
public class GetCampaignInfoNegativeTest {

    private static final User GUEST = SIMPLE_USER_1;
    private static final int ADVERTISER_ID = 199;
    private static final int CAMPAIGN_ID = 268;

    @Test
    @Title("Случайный пользователь не может получить информацию о чужой кампании")
    public void getCampaignsByAdvertiser() {
        UserSteps.withUser(GUEST).onCampaignsSteps().getCampaignInfoAndExpectError(ADVERTISER_ID, CAMPAIGN_ID, ACCESS_DENIED);
    }
}
