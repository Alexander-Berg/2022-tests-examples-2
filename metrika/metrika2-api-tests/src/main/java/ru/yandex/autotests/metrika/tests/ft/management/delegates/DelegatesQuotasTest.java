package ru.yandex.autotests.metrika.tests.ft.management.delegates;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.DelegateE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER_ONLY_FOR_QUOTAS;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATE;
import static ru.yandex.autotests.metrika.errors.ManagementError.DELEGATE_QUOTA_EXCEEDING;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.DELEGATE)
@Title("Проверка квот на добавление представителей")
public class DelegatesQuotasTest {

    private final User OWNER = SIMPLE_USER_ONLY_FOR_QUOTAS;
    private final User DELEGATE = USER_DELEGATE;

    private UserSteps firstUserOwner;

    @Before
    public void setup() {
        firstUserOwner = new UserSteps().withUser(OWNER);
    }

    @Test
    @Title("Проверка квот на добавление представителей")
    public void check() {
        // default quota = 3 and multiplier of SIMPLE_USER_ONLY_FOR_QUOTAS = 0, total = 3 * 0 = 0
        firstUserOwner.onManagementSteps().onDelegatesSteps().addDelegateAndExpectError(DELEGATE_QUOTA_EXCEEDING,
                new DelegateE().withUserLogin(DELEGATE.get(LOGIN)).withComment("Test comment"));
    }
}
