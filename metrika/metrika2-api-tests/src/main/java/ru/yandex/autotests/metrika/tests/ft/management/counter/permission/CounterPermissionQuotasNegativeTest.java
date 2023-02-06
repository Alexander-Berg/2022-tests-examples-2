package ru.yandex.autotests.metrika.tests.ft.management.counter.permission;

import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;
import static ru.yandex.autotests.metrika.errors.ManagementError.GRANTS_QUOTA_EXCEEDING;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounterWithViewPermission;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.COUNTERS, Requirements.Story.Management.PERMISSION})
@Title("Проверка квот при создании счетчиков с гостевыми доступами")
public class CounterPermissionQuotasNegativeTest {
    private static final User OWNER = Users.SIMPLE_USER;
    private static final User OTHER1 = Users.SIMPLE_USER2;
    private static final User OTHER2 = Users.SIMPLE_USER3;
    private static final User OTHER3 = Users.USER_FOR_EMAIL_SUBSCRIPTION1;
    private static final User OTHER4 = Users.USER_FOR_EMAIL_SUBSCRIPTION2;
    private UserSteps user;

    @Test
    @Title("Квоты при создании (негативный)")
    public void createCounterWithPermissions() {
        user = new UserSteps().withUser(OWNER);
        user.onManagementSteps().onCountersSteps().addCounterAndExpectError(GRANTS_QUOTA_EXCEEDING, getDefaultCounterWithViewPermission(OTHER1, OTHER2, OTHER3, OTHER4));
    }
}
