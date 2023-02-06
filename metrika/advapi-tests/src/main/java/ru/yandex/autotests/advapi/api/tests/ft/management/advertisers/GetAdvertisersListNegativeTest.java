package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers;

import org.junit.Test;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.parameters.AdvertiserManagementParameters;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.advapi.Errors.INCORRECT_PARAMETER_VALUE;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;

@Features(MANAGEMENT)
@Title("Получение списка рекламодателей (негативные)")
public class GetAdvertisersListNegativeTest {

    private static final User OWNER = SIMPLE_USER_1;

    @Test
    @Title("нельзя фильтровать по некорректному статусу кампаний")
    public void failToGetAdvertisersList() {
        UserSteps.withUser(OWNER).onAdvertisersSteps().getAdvertisersListAndExpectError(INCORRECT_PARAMETER_VALUE, new AdvertiserManagementParameters().withCampaignStatus("incorrect_campaign_status"));
    }
}
