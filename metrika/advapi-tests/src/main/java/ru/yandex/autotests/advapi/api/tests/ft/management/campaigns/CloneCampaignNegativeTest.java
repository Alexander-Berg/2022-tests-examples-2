package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.junit.*;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.metrika.adv.api.management.campaign.external.CampaignSettingsOut;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.Errors.ACCESS_DENIED;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createBaseCampaign;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createSimpleAdvertiser;
import static ru.yandex.autotests.advapi.data.users.Users.*;

@Features(MANAGEMENT)
@Title("Клонирование кампании (негативные)")
@RunWith(Parameterized.class)
public class CloneCampaignNegativeTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final User GUEST = SIMPLE_USER_A;

    private long advertiserId;
    private CampaignSettingsOut campaign;

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public String title;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        GUEST,
                        "случайный пользователь не может клонировать чужую кампанию"
                },
                {
                        SUPERVISOR,
                        "суперсмотритель не может клонировать чужую кампанию"
                },
                {
                        WRITE_GUEST,
                        "пользователь с правами на редактирование не может клонировать чужую кампанию"
                },
                {
                        READ_GUEST,
                        "пользователь с правами на чтение не может клонировать чужую кампанию"
                }
        });
    }

    @Before
    public void setUp() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
        campaign = createBaseCampaign(OWNER, advertiserId);
    }

    @Test
    public void failToCloneCampaign() {
        UserSteps.withUser(user).onCampaignsSteps().cloneCampaignAndExpectError(advertiserId, campaign.getCampaignId(), ACCESS_DENIED);
    }

    @After
    public void cleanUp() {
        UserSteps.withUser(OWNER).onCampaignsSteps().deleteCampaignAndExpectSuccess(advertiserId, campaign.getCampaignId());
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
