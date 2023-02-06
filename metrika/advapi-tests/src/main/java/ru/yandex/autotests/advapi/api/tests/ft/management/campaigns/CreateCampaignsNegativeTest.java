package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.advapi.V1ManagementAdvertiserAdvertiserIdCampaignsPOSTRequestSchema;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.adv.api.management.campaign.external.CampaignSettingsIn;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.Errors.*;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.getPlainCampaign;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.getTooLongName;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_A;

@Features(MANAGEMENT)
@Title("Создания кампании (негативные)")
@RunWith(Parameterized.class)
public class CreateCampaignsNegativeTest {

    private static final UserSteps OWNER = UserSteps.withUser(SIMPLE_USER_1);
    private static final UserSteps GUEST = UserSteps.withUser(SIMPLE_USER_A);
    private static final long ADVERTISER_196 = 196L;
    private static final long ADVERTISER_202 = 202L;

    @Parameterized.Parameter()
    public UserSteps user;

    @Parameterized.Parameter(1)
    public long advertiserId;

    @Parameterized.Parameter(2)
    public CampaignSettingsIn campaign;

    @Parameterized.Parameter(3)
    public IExpectedError error;

    @Parameterized.Parameter(4)
    public String title;

    @Parameterized.Parameters(name = "{4}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        OWNER,
                        ADVERTISER_202,
                        getPlainCampaign().withPlacements(null),
                        MAY_NOT_BE_EMPTY,
                        "нельзя создать кампанию без размещения"
                },
                {
                        OWNER,
                        ADVERTISER_202,
                        getPlainCampaign().withDateStart(null),
                        MAY_NOT_BE_NULL,
                        "нельзя создать кампанию без даты старта"
                },
                {
                        OWNER,
                        ADVERTISER_202,
                        getPlainCampaign().withViewabilityStandard(null),
                        MAY_NOT_BE_NULL,
                        "нельзя создать кампанию без указания способа измерения видимости"
                },
                {
                        OWNER,
                        ADVERTISER_202,
                        getPlainCampaign().withName(""),
                        SIZE_MUST_BE_BETWEEN,
                        "нельзя создать кампанию без имени"
                },
                {
                        OWNER,
                        ADVERTISER_202,
                        getPlainCampaign().withName(getTooLongName()),
                        SIZE_MUST_BE_BETWEEN,
                        "нельзя создать кампанию с именем, длинее 256 символа"
                },
                {
                        OWNER,
                        ADVERTISER_202,
                        getPlainCampaign().withDateEnd(null),
                        MAY_NOT_BE_NULL,
                        "нельзя создать кампанию без даты завешения"
                },
                {
                        GUEST,
                        ADVERTISER_196,
                        new CampaignSettingsIn(),
                        ACCESS_DENIED,
                        "нельзя создать кампанию без наличия доступа к рекламодателю"
                }
        });
    }

    @Test
    public void failToCreateCampaign() {
        V1ManagementAdvertiserAdvertiserIdCampaignsPOSTRequestSchema body = new V1ManagementAdvertiserAdvertiserIdCampaignsPOSTRequestSchema().withCampaign(campaign);
        user.onCampaignsSteps().addCampaignAndExpectError(advertiserId, body, error);
    }
}
