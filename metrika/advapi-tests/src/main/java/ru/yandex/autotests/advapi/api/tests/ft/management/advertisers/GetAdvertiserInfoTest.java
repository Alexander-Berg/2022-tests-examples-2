package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.CompareStrategy;
import ru.yandex.metrika.adv.api.management.advertiser.external.AdvertiserInfo;
import ru.yandex.metrika.api.Feature;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Collections;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.ADVERTISER_INFO_196_BEAN;
import static ru.yandex.autotests.advapi.data.users.Users.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer2.BeanDifferMatcher.beanDiffer;
import static ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath.newPath;
import static ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategies.allFieldsExcept;

@Features(MANAGEMENT)
@Title("Получения информации о рекламодателе")
@RunWith(Parameterized.class)
public class GetAdvertiserInfoTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final long ADVERTISER_196 = 196L;
    private static final CompareStrategy STRATEGY = allFieldsExcept(newPath("activeCampaignsCnt"), newPath("archivedCampaignsCnt"));

    private AdvertiserInfo advertiserInfo;

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public String message;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {OWNER, SIMPLE_USER_1 + " имеет доступ к рекламодателю 196"},
                {SUPER_USER, SUPER_USER + " имеет доступ к рекламодателю 196"},
                {SUPERVISOR, SUPERVISOR + " имеет доступ к рекламодателю 196"}
        });
    }

    @Before
    public void setUp() {
        advertiserInfo = UserSteps.withUser(user).onAdvertisersSteps().getAdvertiserInfoAndExpectSuccess(ADVERTISER_196).getAdvertiser();
    }

    @Test
    public void getAdvertiserInfo() {
        assertThat(message, advertiserInfo, beanDiffer(getExpectedBean(ADVERTISER_INFO_196_BEAN, user)).useCompareStrategy(STRATEGY));
    }

    private AdvertiserInfo getExpectedBean(AdvertiserInfo bean, User user) {
        if (user.equals(SUPER_USER) || user.equals(SUPERVISOR)) {
            return bean.withFeatures(Collections.singletonList(Feature.OFFLINE_REACH));
        }
        return bean.withFeatures(Collections.emptyList());
    }
}
