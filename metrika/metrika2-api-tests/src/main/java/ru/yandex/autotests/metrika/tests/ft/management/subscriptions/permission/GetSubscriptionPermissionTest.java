package ru.yandex.autotests.metrika.tests.ft.management.subscriptions.permission;

import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

import com.hazelcast.core.ILock;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.subscriptions.Subscription;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPER_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPPORT;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SUBSCRIPTION)
@Title("Проверка прав чтения подписки пользователя")
@RunWith(Parameterized.class)
public class GetSubscriptionPermissionTest {
    private static final UserSteps USER = new UserSteps().withUser(Users.SIMPLE_USER);

    private static final User MANAGER = Users.MANAGER;

    private Optional<ILock> lock;

    private String email = "test@test.ru";

    @Parameterized.Parameter(0)
    public String userTitle;

    @Parameterized.Parameter(1)
    public User currentUser;

    @Parameterized.Parameters(name = "Пользователь: {0}")
    public static Collection<Object[]> createParameters() {
        return asList(
                new Object[][]{
                        {"super", SUPER_USER},
                        {"support", SUPPORT},
                        {"менеджер", MANAGER}
                }
        );
    }

    @Before
    public void setup() {
        this.lock = USER.onManagementSteps().onSubscriptionsSteps().getLock();
        USER.onManagementSteps().onSubscriptionsSteps().addClearUserWithDeleteBefore(email);

        USER.onManagementSteps().onSubscriptionsSteps().changeSubscription(SubscriptionType.PROMO, true, SubscriptionListType.ALL, Collections.emptyList());
    }

    @Test
    public void checkSubscription() {
        final List<Subscription> subscriptions =
                new UserSteps().withUser(currentUser).onManagementSteps().onSubscriptionsSteps().getSubscriptions(Users.SIMPLE_USER.get(User.UID));
        final Subscription subscription =
                subscriptions.stream().filter(s -> s.getType() == SubscriptionType.PROMO).findAny().get();
        assertThat("вернулась корректная информация по подписке", subscription, beanEquivalent(new Subscription()
                .withType(SubscriptionType.PROMO)
                .withSubscriptionListType(SubscriptionListType.ALL)
                .withEnabled(true)
                .withCounterIds(Collections.emptyList())
        ));
    }

    @After
    public void teardown() {
        lock.ifPresent(ILock::unlock);
    }
}
