package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers.multiplier;

import java.util.Collection;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createSimpleAdvertiser;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.getGrantMultiplier;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;
import static ru.yandex.autotests.advapi.data.users.Users.SUPERVISOR;
import static ru.yandex.autotests.advapi.data.users.Users.SUPER_USER;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;

@Features(MANAGEMENT)
@Title("Получение множителя для квот, предназначенная для работы с грантами рекламодателя")
@RunWith(Parameterized.class)
public class GetAdvertiserGrantMultiplierTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final User SUPER = SUPER_USER;
    long advertiserId;

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public String message;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {SIMPLE_USER_1, SIMPLE_USER_1 + " является владельцем рекламодателя"},
                {SUPER_USER, SUPER_USER + " является суперюзером"},
                {SUPERVISOR, SUPERVISOR + " является супервизором"}
        });
    }

    @Before
    public void setUp() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
    }

    @Test
    public void getAdvertiserGrantMultiplier() {
        assertThat("Дефолтный множитель должен быть равен = 1.0", getGrantMultiplier(user, advertiserId), beanEquivalent(1.0));
    }

    @After
    public void cleanUp() {
        UserSteps.withUser(SUPER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
