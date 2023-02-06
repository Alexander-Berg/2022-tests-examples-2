package ru.yandex.autotests.advapi.api.tests.ft.management.placements;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.*;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;

@Features(MANAGEMENT)
@Title("Удаление размещений")
public class DeletePlacementTest {

    private static final User OWNER = SIMPLE_USER_1;

    private static long advertiserId;
    private static long campaignId;
    private static long placementId;

    @BeforeClass
    public static void create() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
        campaignId = createBaseCampaign(OWNER, advertiserId).getCampaignId();
        UserSteps.withUser(OWNER).onPlacementsSteps().addPlacementsAndExpectSuccess(advertiserId, campaignId, getSimplePlacement());
        placementId = UserSteps.withUser(OWNER).onPlacementsSteps().addPlacementsAndExpectSuccess(advertiserId, campaignId, getSimplePlacement()).getPlacement().getPlacementId();
    }

    @Test
    public void deletePlacement() {
        UserSteps.withUser(OWNER).onPlacementsSteps().deletePlacementAndExpectSuccess(advertiserId, campaignId, placementId);
    }

    @AfterClass
    public static void destroy() {
        UserSteps.withUser(OWNER).onCampaignsSteps().deleteCampaignAndExpectSuccess(advertiserId, campaignId);
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
