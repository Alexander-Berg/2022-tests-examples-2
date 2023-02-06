package ru.yandex.autotests.advapi.api.tests.ft.management.advertisers;

import org.junit.Before;
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
import static ru.yandex.autotests.advapi.api.tests.ft.management.ManagementTestUtils.createSimpleAdvertiser;
import static ru.yandex.autotests.advapi.data.users.Users.SIMPLE_USER_1;
import static ru.yandex.autotests.advapi.data.users.Users.SUPER_USER;

@Features(MANAGEMENT)
@Title("Удаления рекламодателя")
@RunWith(Parameterized.class)
public class DeleteAdvertiserTest {

    private static final User OWNER = SIMPLE_USER_1;

    public long advertiserId;

    @Parameterized.Parameter()
    public User user;

    @Parameterized.Parameter(1)
    public String message;

    @Parameterized.Parameters(name = "{1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {OWNER, "владелец может удалять своих рекламодателей"},
                {SUPER_USER, "суперпользователь может удалять не своих рекламодателей"}
        });
    }

    @Before
    public void setUp() {
        advertiserId = createSimpleAdvertiser(OWNER).getAdvertiserId();
    }

    @Test
    public void deleteAdvertiser() {
        UserSteps.withUser(user).onAdvertisersSteps().deleteAdvertiserAndExpectSuccess(advertiserId);
    }
}
