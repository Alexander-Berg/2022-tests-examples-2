package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategy;
import ru.yandex.metrika.adv.api.management.advertiser.external.AdvertiserSettings;
import ru.yandex.metrika.api.Feature;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Collections;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.ADVERTISER_196_BEAN;
import static ru.yandex.autotests.advapi.data.users.Users.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer2.BeanDifferMatcher.beanDiffer;
import static ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath.newPath;
import static ru.yandex.autotests.irt.testutils.beandiffer2.comparestrategy.defaultcomparestrategy.DefaultCompareStrategies.allFieldsExcept;

@Features(MANAGEMENT)
@Title("Получение рекламодателя")
@RunWith(Parameterized.class)
public class GetAdvertiserTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final long ADVERTISER_ID = 196L;
    private static final DefaultCompareStrategy STRATEGY = allFieldsExcept(newPath("permission"));

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public String message;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {OWNER, "владелец может получить своего рекламодателя"},
                {SUPERVISOR, "суперсмотритель может получить чужого рекламодателя"},
                {SUPER_USER, "суперпользователь может получить чужого рекламодателя"},
                {READ_GUEST, "пользователь с правами на чтение может получить чужого рекламодателя"},
                {WRITE_GUEST, "пользователь с правами на запись может получить чужого рекламодателя"}
        });
    }

    @Test
    public void getAdvertiser() {
        assertThat(message, UserSteps.withUser(user).onAdvertisersSteps().getAdvertiserAndExpectSuccess(ADVERTISER_ID).getAdvertiser(), beanDiffer(getExpectedBean(ADVERTISER_196_BEAN, user)).useCompareStrategy(STRATEGY));
    }

    private AdvertiserSettings getExpectedBean(AdvertiserSettings bean, User user) {
        if (user.equals(SUPER_USER) || user.equals(SUPERVISOR)) {
            return bean.withFeatures(Collections.singletonList(Feature.OFFLINE_REACH));
        }
        return bean.withFeatures(Collections.emptyList());
    }
}
