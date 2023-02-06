package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

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
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.CAMPAIGN_INFO_256_BEAN;
import static ru.yandex.autotests.advapi.data.users.Users.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer2.BeanDifferMatcher.beanDiffer;

@Features(MANAGEMENT)
@Title("Получения информации о кампании")
@RunWith(Parameterized.class)
public class GetCampaignInfoTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final long ADVERTISER_ID = 196;
    private static final long CAMPAIGN_ID = 256;

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public String message;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {OWNER, "владелец может получить инфомацию о кампании"},
                {READ_GUEST, "пользователь с правами на чтение может получить свою кампанию"},
                {WRITE_GUEST, "пользователь с правами на редактирование может получить свою кампанию"},
                {SUPER_USER, "суперпользователь может получить инфомацию о кампании"},
                {SUPERVISOR, "суперсмотритель может получить инфомацию о кампании"}
        });
    }

    @Test
    public void getCampaignInfo() {
        assertThat(message, UserSteps.withUser(user).onCampaignsSteps().getCampaignInfoAndExpectSuccess(ADVERTISER_ID, CAMPAIGN_ID).getCampaign(), beanDiffer(CAMPAIGN_INFO_256_BEAN));
    }
}
