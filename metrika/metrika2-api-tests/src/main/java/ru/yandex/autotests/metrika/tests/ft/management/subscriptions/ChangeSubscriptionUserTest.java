package ru.yandex.autotests.metrika.tests.ft.management.subscriptions;

import java.util.Collections;
import java.util.List;
import java.util.Optional;

import com.hazelcast.core.ILock;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.autotests.metrika.steps.management.SubscriptionsSteps;
import ru.yandex.metrika.api.management.client.subscriptions.Subscription;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionAccountStatus;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionType;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionUser;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.containsInAnyOrder;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Stories(Requirements.Story.Management.SUBSCRIPTION)
@Title("Проверка включения подписки для пользователя")
public class ChangeSubscriptionUserTest {

    private static final UserSteps USER = new UserSteps().withUser(Users.SIMPLE_USER);
    private Optional<ILock> lock;

    private final String oldEmail = "test@test.ru";
    private final String newEmail = "test2@test.ru";
    private SubscriptionsSteps subscriptionsSteps;

    @Before
    public void setup() {
        this.subscriptionsSteps = USER.onManagementSteps().onSubscriptionsSteps();
        this.lock = subscriptionsSteps.getLock();
        subscriptionsSteps.deleteUserSilent();

        subscriptionsSteps.addUser(oldEmail);
        subscriptionsSteps.changeSubscription(SubscriptionType.API_NEWS, true, SubscriptionListType.ALL, Collections.emptyList());

        subscriptionsSteps.changeEmail(newEmail);
    }

    @Test
    public void checkEmailChanged() {
        final SubscriptionUser user = subscriptionsSteps.getUser();
        assertThat("вернулась корректная информация по подписанному пользователю", user, beanEquivalent(new SubscriptionUser()
                .withEmail(newEmail)
                .withLanguage("ru")
                .withStatus(SubscriptionAccountStatus.SUBSCRIBED)
        ));
    }

    @Test
    public void checkSubscriptionsSaved() {
        final List<Subscription> subscriptions = subscriptionsSteps.getSubscriptions();
        assertThat("вернулась корректная информация по подпискам", subscriptions, containsInAnyOrder(
                    beanEquivalent(subscription(SubscriptionType.API_NEWS, true)),
                    beanEquivalent(subscription(SubscriptionType.COUNTER_ADVICES, false)),
                    beanEquivalent(subscription(SubscriptionType.OTHER_OFFERS, false)),
                    beanEquivalent(subscription(SubscriptionType.PROMO, false))
                )
        );
    }

    @After
    public void teardown() {
        lock.ifPresent(ILock::unlock);
    }

    private Subscription subscription(SubscriptionType type, boolean enabled) {
        return new Subscription()
                .withType(type)
                .withEnabled(enabled)
                ;
    }
}
