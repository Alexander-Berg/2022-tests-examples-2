package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createBaseCampaign;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createSimpleAdvertiser;
import static ru.yandex.autotests.advapi.data.users.Users.*;

@Features(MANAGEMENT)
@Title("Удаление кампании")
@RunWith(Parameterized.class)
public class DeleteCampaignTest {

    private static final User OWNER = SIMPLE_USER_1;

    private static long advertiserId;

    private int campaignId;

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public String message;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {OWNER, "владелец может удалять свои кампании"},
                {WRITE_GUEST, "пользователь с правами на редактирование может удалять кампании, на которые у него есть права"},
                {SUPER_USER, "cуперпользователь может удалять чужие кампании"}
        });
    }

    @BeforeClass
    public static void create() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
    }

    @Before
    public void setUp() {
        campaignId = createBaseCampaign(OWNER, advertiserId).getCampaignId().intValue();
    }

    @Test
    public void deleteCampaign() {
        UserSteps.withUser(user).onCampaignsSteps().deleteCampaignAndExpectSuccess(advertiserId, campaignId);
    }

    @AfterClass
    public static void destroy() {
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
