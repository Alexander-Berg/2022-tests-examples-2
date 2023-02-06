package ru.yandex.autotests.advapi.api.tests.ft.management.campaigns;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategy;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.CAMPAIGN_256_BEAN;
import static ru.yandex.autotests.advapi.data.users.Users.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer2.BeanDifferMatcher.beanDiffer;
import static ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath.newPath;
import static ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategies.allFieldsExcept;

@Features(MANAGEMENT)
@Title("Получение кампании")
@RunWith(Parameterized.class)
public class GetCampaignTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final long ADVERTISER_ID = 196;
    private static final long CAMPAIGN_ID = 256;
    private static final DefaultCompareStrategy STRATEGY = allFieldsExcept(newPath("placements", "0", "site", "siteType"));

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public String message;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {OWNER, "владелец может получить свою кампанию"},
                {READ_GUEST, "пользователь с правами на чтение может получить свою кампанию"},
                {WRITE_GUEST, "пользователь с правами на редактирование может получить свою кампанию"},
                {SUPER_USER, "cуперпользователь может получить не свою кампанию"},
                {SUPERVISOR, "cуперсмотритель может получить не свою кампанию"}
        });
    }

    @Test
    public void getCampaign() {
        assertThat(message, UserSteps.withUser(user).onCampaignsSteps().getCampaignAndExpectSuccess(ADVERTISER_ID, CAMPAIGN_ID).getCampaign(), beanDiffer(CAMPAIGN_256_BEAN).useCompareStrategy(STRATEGY));
    }
}
