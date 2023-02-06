package ru.yandex.autotests.metrika.tests.ft.management.counter.quota;

import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.errors.ManagementError.USER_QUOTA_EXCEEDING;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка корректности ошибки при превышении квоты по пользователю")
public class UserQuotaExceedTest {

    private UserSteps user = new UserSteps().withUser(Users.NO_QUOTA_USER);

    @Test
    public void listCounters() {
        user.onManagementSteps().onCountersSteps()
                .getAvailableCountersAndExpectError(USER_QUOTA_EXCEEDING);
    }
}
