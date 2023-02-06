package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.hamcrest.Matcher;
import org.joda.time.LocalDate;
import org.joda.time.format.DateTimeFormat;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.advapi.V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPUTRequestSchema;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.parameters.CampaignManagementParameters;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.metrika.adv.api.management.campaign.CampaignStatus;
import ru.yandex.metrika.adv.api.management.campaign.external.CampaignSettingsIn;
import ru.yandex.metrika.adv.api.management.campaign.external.CampaignSettingsOut;
import ru.yandex.metrika.adv.api.management.goals.AdvGoal;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.text.SimpleDateFormat;
import java.util.Collection;
import java.util.Date;

import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static org.hamcrest.Matchers.*;
import static org.hamcrest.Matchers.hasProperty;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createBaseCampaign;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.getPlainCampaign;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(MANAGEMENT)
@Title("Изменение кампании")
@RunWith(Parameterized.class)
public class UpdateCampaignTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final long ADVERTISER_ID = 202;
    private static final CampaignManagementParameters OVERRIDE_PARAM = new CampaignManagementParameters().withOverride(true);
    private static final CampaignManagementParameters EMPTY_PARAM = new CampaignManagementParameters();

    private CampaignSettingsOut campaign;

    @Parameterized.Parameter()
    public CampaignSettingsIn update;

    @Parameterized.Parameter(1)
    public Matcher matcher;

    @Parameterized.Parameter(2)
    public String message;

    @Parameterized.Parameter(3)
    public IFormParameters parameters;

    @Parameterized.Parameters(name = "{2}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        getPlainCampaign().withName("test_campaign_updated_" + new SimpleDateFormat("yyyyMMddHHmmssSSS").format(new Date())),
                        hasProperty("name", startsWith("test_campaign_updated_")),
                        "редактирование поля `name`",
                        EMPTY_PARAM
                },
                {
                        getPlainCampaign().withDateEnd(DateTimeFormat.forPattern("yyyy-MM-dd").print(LocalDate.now().plusDays(1))),
                        hasProperty("dateEnd", equalTo(DateTimeFormat.forPattern("yyyy-MM-dd").print(LocalDate.now().plusDays(1)))),
                        "редактирование поля `dateEnd`",
                        EMPTY_PARAM
                },
                {
                        getPlainCampaign().withPlanClicks(17L),
                        hasProperty("planClicks", equalTo(17L)),
                        "редактирование поля `planClicks`",
                        EMPTY_PARAM
                },
                {
                        getPlainCampaign().withStatus(CampaignStatus.ARCHIVED),
                        hasProperty("status", equalTo(CampaignStatus.ARCHIVED)),
                        "редактирование поля `status`",
                        EMPTY_PARAM
                },
                {
                        getPlainCampaign().withGoals(singletonList(new AdvGoal().withCounterId(1L).withGoalId(1L))),
                        hasProperty("goals", contains(allOf(hasProperty("counterId", equalTo(1L)), hasProperty("goalId", equalTo(1L))))),
                        "редактирование поля `goals`",
                        EMPTY_PARAM
                },
                {
                        getPlainCampaign().withPlanCpc(null),
                        allOf(hasProperty("planCpc", equalTo(null)), hasProperty("planClicks", equalTo(199L))),
                        "удалить поле `plan cpc` если параметр override = true",
                        OVERRIDE_PARAM
                },
                {
                        getPlainCampaign().withPlanCpc(null),
                        allOf(hasProperty("planCpc", equalTo(9.9)), hasProperty("planClicks", equalTo(199L))),
                        "нельзя удалить поле `plan cpc` если параметр override = false",
                        EMPTY_PARAM
                }
        });
    }

    @Test
    public void createCampaign() {
        V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPUTRequestSchema body = new V1ManagementAdvertiserAdvertiserIdCampaignCampaignIdPUTRequestSchema().withCampaign(update);
        assertThat(
                message,
                UserSteps.withUser(OWNER).onCampaignsSteps().updateCampaignAndExpectSuccess(ADVERTISER_ID, campaign.getCampaignId().intValue(), body, parameters).getCampaign(),
                matcher
        );
    }

    @Before
    public void setUp() {
        campaign = createBaseCampaign(OWNER, ADVERTISER_ID);
    }

    @After
    public void cleanUp() {
        UserSteps.withUser(OWNER).onCampaignsSteps().deleteCampaignAndExpectSuccess(ADVERTISER_ID, campaign.getCampaignId().intValue());
    }
}
