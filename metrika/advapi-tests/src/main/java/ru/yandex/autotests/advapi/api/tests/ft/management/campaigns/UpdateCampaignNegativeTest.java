package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.junit.*;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.advapi.V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPUTRequestSchema;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.adv.api.management.campaign.external.CampaignSettingsIn;
import ru.yandex.metrika.adv.api.management.campaign.external.CampaignSettingsOut;
import ru.yandex.metrika.adv.api.management.goals.AdvGoal;
import ru.yandex.metrika.rbac.Permission;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Collections;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.Errors.*;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.*;
import static ru.yandex.autotests.advapi.data.users.Users.*;

@Features(MANAGEMENT)
@Title("Изменение кампании (негативные)")
@RunWith(Parameterized.class)
public class UpdateCampaignNegativeTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final User GUEST = SIMPLE_USER_A;

    private static long advertiserId;

    private CampaignSettingsOut campaign;
    private V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPUTRequestSchema body;

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public CampaignSettingsIn update;

    @Parameterized.Parameter(2)
    public IExpectedError error;

    @Parameterized.Parameter(3)
    public String title;

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        OWNER,
                        getPlainCampaign().withName(""),
                        SIZE_MUST_BE_BETWEEN,
                        "нельзя установить пустое имя кампании"
                },
                {
                        OWNER,
                        getPlainCampaign().withName(getTooLongName()),
                        SIZE_MUST_BE_BETWEEN,
                        "нельзя установить имя, размер которого превышает 256 символов"
                },
                {
                        OWNER,
                        getPlainCampaign().withPlanImpressions((long) Integer.MAX_VALUE),
                        MUST_BE_LESS_OR_EQUAL,
                        "плановые импрешены не могут быть больше 1 млрд."
                },
                {
                        OWNER,
                        getPlainCampaign().withPlanClicks((long) Integer.MAX_VALUE),
                        MUST_BE_LESS_OR_EQUAL,
                        "плановые клики не могут быть больше 1 млн."
                },
                {
                        OWNER,
                        getPlainCampaign().withGoals(Collections.nCopies(1001, new AdvGoal())),
                        SIZE_MUST_BE_BETWEEN,
                        "количество целей не может превышать 1000"
                },
                {
                        GUEST,
                        getPlainCampaign(),
                        ACCESS_DENIED,
                        "нельзя редактировать чужую кампанию"
                },
                {
                        READ_GUEST,
                        getPlainCampaign(),
                        ACCESS_DENIED,
                        "пользователь с правами на чтение не может редакировать кампании"
                },
                {
                        SUPERVISOR,
                        getPlainCampaign(),
                        ACCESS_DENIED,
                        "суперпользователь не может редактировать чужую кампанию"
                }
        });
    }

    @BeforeClass
    public static void create() {
        advertiserId = createAdvertiser(OWNER, getAdvertiserSettings(READ_GUEST, Permission.VIEW)).getAdvertiserId();
    }

    @Before
    public void setUp() {
        campaign = createBaseCampaign(OWNER, advertiserId);
        body = new V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPUTRequestSchema().withCampaign(update);
    }

    @Test
    public void failToCreateCampaign() {
        UserSteps.withUser(user).onCampaignsSteps().updateCampaignAndExpectError(advertiserId, campaign.getCampaignId().intValue(), body, error);
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
