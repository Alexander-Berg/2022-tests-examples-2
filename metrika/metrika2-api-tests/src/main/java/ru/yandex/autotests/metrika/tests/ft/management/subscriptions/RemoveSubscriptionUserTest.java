package ru.yandex.autotests.metrika.tests.ft.management.subscriptions;

import java.util.Optional;

import com.hazelcast.core.ILock;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionAccountStatus;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionUser;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Stories(Requirements.Story.Management.SUBSCRIPTION)
@Title("Проверка отключения подписки для пользователя")
public class RemoveSubscriptionUserTest {

    private static final UserSteps USER = new UserSteps().withUser(Users.SIMPLE_USER);
    private Optional<ILock> lock;

    private String email = "test@test.ru";

    @Before
    public void setup() {
        this.lock = USER.onManagementSteps().onSubscriptionsSteps().getLock();
        USER.onManagementSteps().onSubscriptionsSteps().addClearUserWithDeleteBefore(email);
        USER.onManagementSteps().onSubscriptionsSteps().deleteUser();
    }

    @Test
    public void checkUnsubscribed() {
        final SubscriptionUser user = USER.onManagementSteps().onSubscriptionsSteps().getUser();
        assertThat("вернулась корректная информация по подписанному пользователю", user, beanEquivalent(new SubscriptionUser()
                .withEmail(email)
                .withLanguage("ru")
                .withStatus(SubscriptionAccountStatus.UNSUBSCRIBED)
        ));
    }

    @After
    public void teardown() {
        lock.ifPresent(ILock::unlock);
    }
}
