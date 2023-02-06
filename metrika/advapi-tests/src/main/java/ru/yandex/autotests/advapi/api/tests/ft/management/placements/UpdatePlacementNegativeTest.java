package ru.yandex.autotests.advapi.api.tests.ft.management.placements;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.adv.api.management.placement.PlacementType;
import ru.yandex.metrika.adv.api.management.placement.external.PlacementIn;
import ru.yandex.metrika.adv.api.management.placement.external.PlacementOut;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.Errors.*;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.*;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;

@Features(MANAGEMENT)
@Title("Изменение размещений (негативные)")
@RunWith(Parameterized.class)
public class UpdatePlacementNegativeTest {

    private static final User OWNER = SIMPLE_USER_1;

    private static long advertiserId;
    private static long campaignId;
    private static PlacementOut origin;

    @Parameterized.Parameter()
    public PlacementIn update;

    @Parameterized.Parameter(1)
    public IExpectedError error;

    @Parameterized.Parameter(2)
    public String message;

    @Parameterized.Parameters(name = "{2}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        getSimplePlacement().withName(getTooLongName()),
                        SIZE_MUST_BE_BETWEEN,
                        "имя не может быть больше 256 символов"
                },
                {
                        getSimplePlacement().withName(""),
                        SIZE_MUST_BE_BETWEEN,
                        "имя не может быть пустым"
                },
                {
                        getSimplePlacement().withVolume(1_000_000_001L),
                        MUST_BE_LESS_OR_EQUAL,
                        "объем закупок не может превышать 1_000_000_000"
                },
                {
                        getSimplePlacement().withPlacementType(PlacementType.SEARCH),
                        INCORRECT_PARAMETER_VALUE,
                        "нельзя изменить тип размещения на поисковый"
                }
        });
    }

    @BeforeClass
    public static void create() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
        campaignId = createBaseCampaign(OWNER, advertiserId).getCampaignId();
        origin = UserSteps.withUser(OWNER).onPlacementsSteps().addPlacementsAndExpectSuccess(advertiserId, campaignId, getSimplePlacement()).getPlacement();
    }

    @Test
    public void failToUpdatePlacement() {
        UserSteps.withUser(OWNER).onPlacementsSteps().updatePlacementAndExpectError(advertiserId, campaignId, origin.getPlacementId(), update, error);
    }

    @AfterClass
    public static void destroy() {
        UserSteps.withUser(OWNER).onPlacementsSteps().deletePlacementAndExpectSuccess(advertiserId, campaignId, origin.getPlacementId());
        UserSteps.withUser(OWNER).onCampaignsSteps().deleteCampaignAndExpectSuccess(advertiserId, campaignId);
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
