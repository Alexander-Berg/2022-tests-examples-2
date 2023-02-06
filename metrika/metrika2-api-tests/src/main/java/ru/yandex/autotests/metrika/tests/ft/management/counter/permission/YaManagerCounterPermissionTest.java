package ru.yandex.autotests.metrika.tests.ft.management.counter.permission;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPPORT;
import static ru.yandex.autotests.metrika.data.common.users.Users.YAMANAGER;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithEditPermission;

/**
 * Created by sourx on 23.11.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.COUNTERS, Requirements.Story.Management.PERMISSION})
@Title("Проверка прав доступа yamanager'a к счетчикам ya.metrika ")
public class YaManagerCounterPermissionTest {
    private final Long COUNTER_ID = Counters.YANDEX_DIRECT.get(Counter.ID);
    private UserSteps yamanager;
    private UserSteps support;

    @Before
    public void setup() {
        yamanager = new UserSteps().withUser(YAMANAGER);
        support = new UserSteps().withUser(SUPPORT);
    }

    @Test
    @Title("Я.менеджер имеет доступ к данным счетчика")
    public void checkYaCounterViewPermission() {
        yamanager.onManagementSteps().onCountersSteps().getCounterInfo(COUNTER_ID);
    }

    @Test
    @Title("Я.менеджер не имеет прав на редактирование счетчика")
    public void checkYaCounterEditPermission() {
        yamanager.onManagementSteps().onCountersSteps()
                .editCounterAndExpectError(ManagementError.ACCESS_DENIED, COUNTER_ID, getDefaultCounter());
    }

    @Test
    @Title("Я.менеджер не имеет прав на удаление счетчика")
    public void checkYaCounterDeletePermission() {
        yamanager.onManagementSteps().onCountersSteps()
                .deleteCounterAndExpeсtError(COUNTER_ID, ManagementError.ACCESS_DENIED);
    }

    @Test
    @Title("Support не может добавить гостевые доступы на счетчик, принадлежащий ya-metrika")
    public void checkAddGrant() {
        support.onManagementSteps().onCountersSteps()
                .editCounterAndExpectError(ManagementError.YA_METRIKA_COUNTER_GRANT_ERROR, COUNTER_ID, getDefaultCounterWithEditPermission(SIMPLE_USER));
    }
}
