package ru.yandex.autotests.metrika.tests.ft.management.counter.permission;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;

/**
 * Created by sourx on 02.03.2016.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.COUNTERS, Requirements.Story.Management.PERMISSION})
@Title("Проверка прав удаления счетчика")
@RunWith(Parameterized.class)
public class CounterDeletePermissionTest {
    private UserSteps owner;
    private UserSteps user;
    private Long counterId;

    @Parameterized.Parameter(0)
    public String userTitle;

    @Parameterized.Parameter(1)
    public User currentUser;

    @Parameterized.Parameters(name = "Пользователь: {0}")
    public static Collection<Object[]> createParameters() {
        return asList(
                new Object[][]{
                        {"support", SUPPORT},
                        {"super", SUPER_USER}
                }
        );
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(currentUser);
        owner = new UserSteps().withUser(SIMPLE_USER3);
        counterId = owner.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    @Title("Пользователь: суперпользователь")
    public void checkEditPermission() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
