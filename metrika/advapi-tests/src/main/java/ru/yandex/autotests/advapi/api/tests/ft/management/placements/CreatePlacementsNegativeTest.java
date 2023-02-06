package ru.yandex.autotests.advapi.api.tests.ft.management.placements;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.adv.api.management.creative.Creative;
import ru.yandex.metrika.adv.api.management.placement.PlacementType;
import ru.yandex.metrika.adv.api.management.placement.external.PlacementIn;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static ru.yandex.autotests.advapi.Errors.*;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.*;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;

@Features(MANAGEMENT)
@Title("Создание размещений (негативные)")
@RunWith(Parameterized.class)
public class CreatePlacementsNegativeTest {

    private static final User OWNER = SIMPLE_USER_1;

    private static long advertiserId;
    private static long campaignId;

    @Parameterized.Parameter()
    public PlacementIn settings;

    @Parameterized.Parameter(1)
    public IExpectedError error;

    @Parameterized.Parameter(2)
    public String title;

    @Parameterized.Parameters(name = "{2}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {
                        getSimplePlacement().withSiteId(null),
                        MAY_NOT_BE_NULL,
                        "нельзя создать кампанию без ID площадки"
                },
                {
                        getSimplePlacement().withLandingId(null),
                        MAY_NOT_BE_NULL,
                        "нельзя создать кампанию без ID посадочной страницы"
                },
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
                        "нельзя создать размещение поискового типа"
                },
                {
                        getSimplePlacement().withCreatives(singletonList(new Creative().withComment(""))),
                        MAY_NOT_BE_EMPTY,
                        "нельзя создать креатив без имени (поле comment)"
                }
        });
    }

    @BeforeClass
    public static void create() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
        campaignId = createBaseCampaign(OWNER, advertiserId).getCampaignId();
    }

    @Test
    public void failToCreatePlacement() {
        UserSteps.withUser(OWNER).onPlacementsSteps().addPlacementsAndExpectError(advertiserId, campaignId, settings, error);
    }

    @AfterClass
    public static void destroy() {
        UserSteps.withUser(OWNER).onCampaignsSteps().deleteCampaignAndExpectSuccess(advertiserId, campaignId);
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
