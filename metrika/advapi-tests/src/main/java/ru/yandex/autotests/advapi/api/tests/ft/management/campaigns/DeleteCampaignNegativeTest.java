package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.junit.*;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
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
@Title("Удаления кампании (негативные)")
@RunWith(Parameterized.class)
public class DeleteCampaignNegativeTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final User GUEST = SIMPLE_USER_A;

    private static long advertiserId;

    private CampaignSettingsOut campaign;

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public IExpectedError error;

    @Parameterized.Parameter(2)
    public String title;

    @Parameterized.Parameters(name = "{2}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {GUEST, ACCESS_DENIED, "пользоватедль без нужных прав не может удалить чужую кампанию"},
                {READ_GUEST, ACCESS_DENIED, "пользоватедль с правами на чтение не может удалить чужую кампанию"},
                {SUPERVISOR, ACCESS_DENIED, "суперсмотритель не может удалить чужую кампанию"}
        });
    }

    @BeforeClass
    public static void create() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
    }

    @Before
    public void setUp() {
        campaign = createBaseCampaign(OWNER, advertiserId);
    }

    @Test
    public void deleteAdvertiser() {
        UserSteps.withUser(user).onCampaignsSteps().deleteCampaignAndExpectError(advertiserId, campaign.getCampaignId().intValue(), error);
    }

    @After
    public void cleanUp() {
        UserSteps.withUser(OWNER).onCampaignsSteps().deleteCampaignAndExpectSuccess(advertiserId, campaign.getCampaignId().intValue());
    }

    @AfterClass
    public static void destroy() {
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
