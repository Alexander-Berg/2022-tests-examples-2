package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers.multiplier;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.advapi.api.tests.ft.management.AdvApiFeatures.MANAGEMENT;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createSimpleAdvertiser;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.deleteGrantMultiplier;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.getGrantMultiplier;
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.setGrantMultiplier;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;
import static ru.yandex.autotests.advapi.data.users.Users.SUPERVISOR;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;

@Features(MANAGEMENT)
@Title("Удаление множителя для квот, предназначенная для работы с грантами рекламодателя")
public class DeleteAdvertiserGrantMultiplierTest {

    private static final User OWNER = SIMPLE_USER_1;
    private static final User SUPER = SUPERVISOR;

    long advertiserId;

    @Before
    public void setUp() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
    }

    @Test
    public void deleteAdvertiserGrantMultiplier() {
        setGrantMultiplier(SUPER, advertiserId, 10.5);

        deleteGrantMultiplier(SUPER, advertiserId);

        assertThat("После удаления множителя, оно должно равняться к 1.0", getGrantMultiplier(OWNER, advertiserId), beanEquivalent(1.0));
    }

    @After
    public void cleanUp() {
        UserSteps.withUser(OWNER).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
