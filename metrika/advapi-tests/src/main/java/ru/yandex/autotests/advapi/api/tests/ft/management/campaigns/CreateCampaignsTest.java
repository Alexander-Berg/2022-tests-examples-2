package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import com.google.common.collect.Sets;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.advapi.V1ManagementAdvertiserAdvertiserIdCampaignsPOSTRequestSchema;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.metrika.adv.api.management.campaign.external.CampaignSettingsIn;
import ru.yandex.metrika.adv.api.management.campaign.external.CampaignSettingsOut;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createSimpleAdvertiser;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.getPlainCampaign;
import static ru.yandex.autotests.advapi.data.users.Users.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(MANAGEMENT)
@Title("Создание кампании")
public class CreateCampaignsTest {

    private static final User OWNER = SIMPLE_USER_1;

    private static long advertiserId;
    private static CampaignSettingsIn settings;
    private static CampaignSettingsOut campaign;

    @BeforeClass
    public static void setUp() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
        settings = getPlainCampaign();
        V1ManagementAdvertiserAdvertiserIdCampaignsPOSTRequestSchema body = new V1ManagementAdvertiserAdvertiserIdCampaignsPOSTRequestSchema().withCampaign(settings);
        campaign = UserSteps.withUser(OWNER).onCampaignsSteps().addCampaignAndExpectSuccess(advertiserId, body).getCampaign();
    }

    @Test
    public void checkNotNull() {
        assertThat("рекламодатель создан", campaign, notNullValue(CampaignSettingsOut.class));
    }

    @Test
    public void checkName() {
        assertThat("имя корректно", campaign.getName(), equalTo(settings.getName()));
    }

    @Test
    public void checkStartDate() {
        assertThat("дата начала совпадает", campaign.getDateStart(), equalTo(settings.getDateStart()));
    }

    @Test
    public void checkEndDate() {
        assertThat("дата завешения совпадает", campaign.getDateEnd(), equalTo(settings.getDateEnd()));
    }

    @Test
    public void checkGoalPlans() {
        assertThat("планы по целям совпадают", Sets.newHashSet(campaign.getGoalPlans()), equalTo(Sets.newHashSet(settings.getGoalPlans())));
    }

    @Test
    public void checkGoals() {
        assertThat("список целей совпадает", Sets.newHashSet(campaign.getGoals()), equalTo(Sets.newHashSet(settings.getGoals())));
    }

    @Test
    public void checkPlacement() {
        assertThat("первое размещение совпадает", campaign.getPlacements().get(0).getName(), equalTo(settings.getPlacements().get(0).getName()));
    }

    @Test
    public void checkPlanClicks() {
        assertThat("планы по кликам совпадают", campaign.getPlanClicks(), equalTo(settings.getPlanClicks()));
    }

    @Test
    public void checkPlanCpc() {
        assertThat("планы по CPC совпадают", campaign.getPlanCpc(), equalTo(settings.getPlanCpc()));
    }

    @Test
    public void checkPlanCpm() {
        assertThat("планы по СРМ совпадают", campaign.getPlanCpm(), equalTo(settings.getPlanCpm()));
    }

    @Test
    public void checkSuperUserAccessibility() {
        assertThat("созданная компания доступна для суперпользователя", UserSteps.withUser(SUPER_USER).onCampaignsSteps().getCampaignAndExpectSuccess(advertiserId, campaign.getCampaignId()).getCampaign(), notNullValue(CampaignSettingsOut.class));
    }

    @Test
    public void checkSupervisorAccessibility() {
        assertThat("созданная компания доступна для суперсмотителя", UserSteps.withUser(SUPERVISOR).onCampaignsSteps().getCampaignAndExpectSuccess(advertiserId, campaign.getCampaignId()).getCampaign(), notNullValue(CampaignSettingsOut.class));
    }

    @Test
    public void checkReadPermissionUserAccessibility() {
        assertThat("пользователь с правами на чтение имеет доступ к кампании", UserSteps.withUser(READ_GUEST).onCampaignsSteps().getCampaignAndExpectSuccess(advertiserId, campaign.getCampaignId()).getCampaign(), notNullValue(CampaignSettingsOut.class));
    }

    @Test
    public void checkWritePermissionUserAccessibility() {
        assertThat("пользователь с правами на редактирование имеет доступ к кампании", UserSteps.withUser(WRITE_GUEST).onCampaignsSteps().getCampaignAndExpectSuccess(advertiserId, campaign.getCampaignId()).getCampaign(), notNullValue(CampaignSettingsOut.class));
    }

    @AfterClass
    public static void cleanUp() {
        UserSteps.withUser(OWNER).onCampaignsSteps().deleteCampaignAndExpectSuccess(advertiserId, campaign.getCampaignId());
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
