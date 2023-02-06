package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.junit.*;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategy;
import ru.yandex.metrika.adv.api.management.campaign.external.CampaignSettingsOut;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.containsString;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createBaseCampaign;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createSimpleAdvertiser;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;
import static ru.yandex.autotests.advapi.data.users.Users.SUPER_USER;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer2.BeanDifferMatcher.beanDiffer;
import static ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath.newPath;
import static ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategies.allFieldsExcept;

@Features(MANAGEMENT)
@Title("Клонирование кампании")
@RunWith(Parameterized.class)
public class CloneCampaignTest {

    private static final User OWNER = SIMPLE_USER_1;

    private static long advertiserId;

    private CampaignSettingsOut orig;
    private CampaignSettingsOut clone;
    private DefaultCompareStrategy strategy;

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public String title;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {OWNER, "владелец может клонировать свою кампанию"},
                {SUPER_USER, "суперпользователь может клонировать любую кампанию"}
        });
    }

    @BeforeClass
    public static void create() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
    }

    @Before
    public void setUp() {
        orig = createBaseCampaign(OWNER, advertiserId);
        clone = UserSteps.withUser(user).onCampaignsSteps().cloneCampaignAndExpectSuccess(advertiserId, orig.getCampaignId()).getCampaign();

        // realDateStart и realDateEnd приезжают из campaign_dates с прода, и поэтому могут пересекаться с тем что мы тут понасоздавали
        // и чтобы не было ещё больше спорадических беспричинных падений, не проверяем их
        strategy = allFieldsExcept(newPath("name"), newPath("campaignId"), newPath("createTime"), newPath("realDateStart"), newPath("realDateEnd"), newPath("placements", "0", "placementId"), newPath("placements", "0", "creatives", "0", "creativeId"))
                .forFields(newPath("name")).useMatcher(allOf(containsString(orig.getName()), containsString("копия")));
    }

    @Test
    public void checkCreation() {
        assertThat("кампания склонированна", clone, beanDiffer(orig).useCompareStrategy(strategy));
    }

    @After
    public void cleanUp() {
        UserSteps.withUser(user).onCampaignsSteps().deleteCampaignAndExpectSuccess(advertiserId, clone.getCampaignId());
        UserSteps.withUser(OWNER).onCampaignsSteps().deleteCampaignAndExpectSuccess(advertiserId, orig.getCampaignId());
    }

    @AfterClass
    public static void destroy() {
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
