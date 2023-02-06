package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.parameters.CampaignManagementParameters;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.Errors.ADVERTISER_NOT_FOUND;
import static ru.yandex.autotests.advapi.Errors.INCORRECT_PARAMETER_VALUE;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;

@Features(MANAGEMENT)
@Title("Получение списка кампаний (негативные)")
@RunWith(Parameterized.class)
public class GetCampaignsNegativeTest {

    private static final UserSteps OWNER = UserSteps.withUser(SIMPLE_USER_1);
    private static final long NONEXISTING_ADVERTISER_ID = Integer.MAX_VALUE;

    @Parameterized.Parameter()
    public IExpectedError error;

    @Parameterized.Parameter(1)
    public CampaignManagementParameters parameters;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        ADVERTISER_NOT_FOUND,
                        new CampaignManagementParameters().withAdvertiserId(NONEXISTING_ADVERTISER_ID)
                },
                {
                        INCORRECT_PARAMETER_VALUE,
                        new CampaignManagementParameters().withStatus("incorrect_status")
                },
                {
                        INCORRECT_PARAMETER_VALUE,
                        new CampaignManagementParameters().withSort("incorrect_sort")
                },
                {
                        INCORRECT_PARAMETER_VALUE,
                        new CampaignManagementParameters().withTo("incorrect_to_date").withFrom("incorrect_from_date")
                }
        });
    }

    @Test
    public void failToGetCampaigns() {
        OWNER.onCampaignsSteps().getCampaignsAndExpectError(error, parameters);
    }
}
