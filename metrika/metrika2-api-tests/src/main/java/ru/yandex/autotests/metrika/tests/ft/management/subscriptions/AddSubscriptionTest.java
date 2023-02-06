package ru.yandex.autotests.metrika.tests.ft.management.subscriptions;

import java.util.Arrays;
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
import org.junit.runners.Parameterized.Parameter;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.subscriptions.Subscription;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionType;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@RunWith(Parameterized.class)
@Stories(Requirements.Story.Management.SUBSCRIPTION)
@Title("Проверка включения подписок")
public class AddSubscriptionTest {

    private static final UserSteps USER = new UserSteps().withUser(Users.SIMPLE_USER);
    private Optional<ILock> lock;

    private String email = "test@test.ru";


    @Parameter(0)
    public SubscriptionType subscriptionType;

    @Parameter(1)
    public SubscriptionListType subscriptionListType;

    @Parameter(2)
    public List<Long> counterIds;

    @Parameterized.Parameters(name = "{0}: {1}")
    public static Collection<Object[]> createParameters() {
        return asList(
                new Object[][]{
                        {SubscriptionType.COUNTER_ADVICES, SubscriptionListType.EDIT, Collections.emptyList()},
                        {SubscriptionType.COUNTER_ADVICES, SubscriptionListType.LIST, Arrays.asList(1L,2L,3L)},
                        {SubscriptionType.API_NEWS, SubscriptionListType.ALL, Collections.emptyList()},
                        {SubscriptionType.OTHER_OFFERS, SubscriptionListType.ALL, Collections.emptyList()},
                        {SubscriptionType.PROMO, SubscriptionListType.ALL, Collections.emptyList()}
                }
        );
    }


    @Before
    public void setup() {
        this.lock = USER.onManagementSteps().onSubscriptionsSteps().getLock();
        USER.onManagementSteps().onSubscriptionsSteps().addClearUserWithDeleteBefore(email);

        USER.onManagementSteps().onSubscriptionsSteps().changeSubscription(subscriptionType, true, subscriptionListType, counterIds);
    }

    @Test
    public void checkSubscription() {
        final List<Subscription> subscriptions = USER.onManagementSteps().onSubscriptionsSteps().getSubscriptions();
        final Subscription subscription =
                subscriptions.stream().filter(s -> s.getType() == subscriptionType).findAny().get();

        assertThat("вернулась корректная информация по подписке", subscription, beanEquivalent(new Subscription()
                .withType(subscriptionType)
                .withSubscriptionListType(subscriptionListType)
                .withEnabled(true)
                .withCounterIds(counterIds)
        ));
    }

    @After
    public void teardown() {
        lock.ifPresent(ILock::unlock);
    }
}
