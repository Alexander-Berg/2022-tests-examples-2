package ru.yandex.autotests.advapi.api.tests.ft.management.placements;

import org.hamcrest.Matcher;
import org.junit.*;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.parameters.PlacementManagementParameters;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.metrika.adv.api.management.placement.PricingModel;
import ru.yandex.metrika.adv.api.management.placement.external.PlacementIn;
import ru.yandex.metrika.adv.api.management.placement.external.PlacementOut;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.*;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;

@Features(MANAGEMENT)
@Title("Изменение размещений")
@RunWith(Parameterized.class)
public class UpdatePlacementTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final IFormParameters OVERRIDE_PARAM = new PlacementManagementParameters().withOverride(true);
    private static final IFormParameters EMPTY_PARAM = new PlacementManagementParameters();

    private static long advertiserId;
    private static long campaignId;

    private PlacementOut origin;

    @Parameterized.Parameter()
    public PlacementIn update;

    @Parameterized.Parameter(1)
    public IFormParameters params;

    @Parameterized.Parameter(2)
    public Matcher matcher;

    @Parameterized.Parameter(3)
    public String message;

    @Parameterized.Parameters(name = "{3}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        getSimplePlacement().withName(getUpdateName("placement")),
                        EMPTY_PARAM,
                        hasProperty("name", startsWith("test_placement_updated_")),
                        "редактирование поля `name` успешно"
                },
                {
                        getSimplePlacement().withVolume(999L),
                        EMPTY_PARAM,
                        hasProperty("volume", equalTo(999L)),
                        "редактирование поля `volume` успешно"
                },
                {
                        getSimplePlacement().withSiteId(5L),
                        EMPTY_PARAM,
                        hasProperty("site", hasProperty("siteId", equalTo(5L))),
                        "редактирование поля `siteId` успешно"
                },
                {
                        getSimplePlacement().withLandingId(166L),
                        EMPTY_PARAM,
                        hasProperty("landing", hasProperty("landingId", equalTo(166L))),
                        "редактирование поля `landingId` успешно"
                },
                {
                        getSimplePlacement().withCost(999.0),
                        EMPTY_PARAM,
                        hasProperty("cost", equalTo(999.0)),
                        "редактирование поля `cost` успешно"
                },
                {
                        getSimplePlacement().withPricingModel(PricingModel.DAYS),
                        EMPTY_PARAM,
                        hasProperty("pricingModel", equalTo(PricingModel.DAYS)),
                        "редактирование поля `pricingModel` успешно"
                },
                {
                        getSimplePlacement().withCost(null),
                        OVERRIDE_PARAM,
                        hasProperty("cost", nullValue()),
                        "удаление поля `cost` с параметром override=true"
                },
                {
                        getSimplePlacement().withVolume(null),
                        OVERRIDE_PARAM,
                        hasProperty("volume", nullValue()),
                        "удаление поля `volume` с параметром override=true"
                },
                {
                        getSimplePlacement().withCost(null),
                        EMPTY_PARAM,
                        hasProperty("cost", equalTo(1d)),
                        "нельзя удалить поле `cost` с параметром override=false"
                },
                {
                        getSimplePlacement().withVolume(null),
                        EMPTY_PARAM,
                        hasProperty("volume", equalTo(10L)),
                        "нельзя удалить поле `volume` с параметром override=false"
                }
        });
    }

    @BeforeClass
    public static void setUp() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
        campaignId = createBaseCampaign(OWNER, advertiserId).getCampaignId();
    }

    @Before
    public void create() {
        origin = UserSteps.withUser(OWNER).onPlacementsSteps().addPlacementsAndExpectSuccess(advertiserId, campaignId, getSimplePlacement()).getPlacement();
    }

    @Test
    public void updatePlacement() {
        assertThat(message, UserSteps.withUser(OWNER).onPlacementsSteps().updatePlacementAndExpectSuccess(advertiserId, campaignId, origin.getPlacementId(), update, params).getPlacement(), matcher);
    }

    @After
    public void delete() {
        UserSteps.withUser(OWNER).onPlacementsSteps().deletePlacementAndExpectSuccess(advertiserId, campaignId, origin.getPlacementId());
    }

    @AfterClass
    public static void destroy() {
        UserSteps.withUser(OWNER).onCampaignsSteps().deleteCampaignAndExpectSuccess(advertiserId, campaignId);
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
