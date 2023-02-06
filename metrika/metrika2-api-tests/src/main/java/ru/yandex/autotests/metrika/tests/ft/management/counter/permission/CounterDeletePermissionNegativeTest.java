package ru.yandex.autotests.metrika.tests.ft.management.counter.permission;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.ignoreQuota;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.*;

/**
 * Created by sourx on 02.03.2016.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.COUNTERS, Requirements.Story.Management.PERMISSION})
@Title("Проверка прав удаления счетчика (негативные)")
@RunWith(Parameterized.class)
public class CounterDeletePermissionNegativeTest {
    private final User OWNER = Users.SIMPLE_USER3;
    private static final User OTHER = Users.SIMPLE_USER;
    private static final User MANAGER = Users.MANAGER;
    private static final User DIRECT = Users.MANAGER_DIRECT;
    private static final User YAMANAGER = Users.YAMANAGER;

    private UserSteps owner;
    private UserSteps user;
    private Long counterId;

    @Parameter(0)
    public String userTitle;

    @Parameter(1)
    public CounterFull counter;

    @Parameter(2)
    public User currentUser;

    @Parameters(name = "Пользователь: {0}")
    public static Collection<Object[]> createParameters() {
        return asList(
                new Object[][]{
                        {"иной пользователь", getDefaultCounter(), OTHER},
                        {"иной пользователь", getDefaultCounterWithPublicStatPermission(), OTHER},
                        {"с правом на редактирование", getDefaultCounterWithEditPermission(OTHER), OTHER},
                        {"с правом на просмотр", getDefaultCounterWithViewPermission(OTHER), OTHER},
                        {"менеджер", getDefaultCounter(), MANAGER},
                        {"менеджер Директа", getDefaultCounter(), DIRECT},
                        {"яндекс менеджер", getDefaultCounter(), YAMANAGER}
                }
        );
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(currentUser);
        owner = new UserSteps().withUser(OWNER);
        counterId = owner.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter,
                ignoreQuota(true)).getId();
    }

    @Test
    public void checkEditPermission() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndExpeсtError(counterId, ACCESS_DENIED);
    }

    @After
    public void teardown() {
        owner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
