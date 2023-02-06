package ru.yandex.autotests.advapi.api.tests.ft.management.placements;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.metrika.adv.api.management.placement.external.PlacementIn;
import ru.yandex.metrika.adv.api.management.placement.external.PlacementOut;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.*;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer2.BeanDifferMatcher.beanDiffer;

@Features(MANAGEMENT)
@Title("Создание размещений")
public class CreatePlacementsTest {

    private static final User OWNER = SIMPLE_USER_1;

    private static long advertiserId;
    private static long campaignId;
    private static PlacementIn settings;
    private static PlacementOut placement;

    @BeforeClass
    public static void create() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
        campaignId = createBaseCampaign(OWNER, advertiserId).getCampaignId();

        settings = getSimplePlacement();
        placement = UserSteps.withUser(OWNER).onPlacementsSteps().addPlacementsAndExpectSuccess(advertiserId, campaignId, settings).getPlacement();
    }

    @Test
    public void checkNotNull() {
        assertThat("размещение созданно", placement, notNullValue(PlacementOut.class));
    }

    @Test
    public void checkName() {
        assertThat("имя корректно", placement.getName(), equalTo(settings.getName()));
    }

    @Test
    public void checkPlacementType() {
        assertThat("тип размещения banner", placement.getPlacementType(), equalTo(settings.getPlacementType()));
    }

    @Test
    public void checkPricingModel() {
        assertThat("единица закупки CPC", placement.getPricingModel(), equalTo(settings.getPricingModel()));
    }

    @Test
    public void checkVolume() {
        assertThat("объем закупки 0", placement.getVolume(), equalTo(settings.getVolume()));
    }

    @Test
    public void checkCost() {
        assertThat("стоимость за единицу 0.0", placement.getCost(), equalTo(settings.getCost()));
    }

    @Test
    public void checkCreatives() {
        assertThat("креативы созданны корректно", placement.getCreatives(), iterableWithSize(1));
    }

    @Test
    public void checkSite() {
        assertThat("площадка 'Яндекс'", placement.getSite(), beanDiffer(SITE_2));
    }

    @Test
    public void checkLanding() {
        assertThat("посадочная страница верна", placement.getLanding(), beanDiffer(LANDING_172));
    }

    @AfterClass
    public static void destroy() {
        UserSteps.withUser(OWNER).onPlacementsSteps().deletePlacementAndExpectSuccess(advertiserId, campaignId, placement.getPlacementId());
        UserSteps.withUser(OWNER).onCampaignsSteps().deleteCampaignAndExpectSuccess(advertiserId, campaignId);
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
