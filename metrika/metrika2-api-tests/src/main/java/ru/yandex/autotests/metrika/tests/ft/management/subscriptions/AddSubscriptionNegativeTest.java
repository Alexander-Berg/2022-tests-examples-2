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
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.subscriptions.Subscription;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionType;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.errors.ManagementError.INCORRECT_VALUE_IN_COLUMN;
import static ru.yandex.autotests.metrika.errors.ManagementError.SUBSCRIPTION_COUNTER_IDS_ONLY_FOR_LIST;
import static ru.yandex.autotests.metrika.errors.ManagementError.SUBSCRIPTION_LIST_ONLY_FOR_COUNTER_ADVICES;
import static ru.yandex.autotests.metrika.errors.ManagementError.SUBSCRIPTION_NOT_ALL_FOR_COUNTER_ADVICES;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@RunWith(Parameterized.class)
@Stories(Requirements.Story.Management.SUBSCRIPTION)
@Title("Проверка включения подписок - негативные")
public class AddSubscriptionNegativeTest {

    private static final UserSteps USER = new UserSteps().withUser(Users.SIMPLE_USER);
    private Optional<ILock> lock;

    private String email = "test@test.ru";


    @Parameter(0)
    public SubscriptionType subscriptionType;

    @Parameter(1)
    public SubscriptionListType subscriptionListType;

    @Parameter(2)
    public List<Long> counterIds;

    @Parameter(3)
    public IExpectedError error;

    @Parameterized.Parameters(name = "{0}: {1}")
    public static Collection<Object[]> createParameters() {
        return asList(
                new Object[][]{
                        {SubscriptionType.COUNTER_ADVICES, SubscriptionListType.ALL, Collections.emptyList(), SUBSCRIPTION_NOT_ALL_FOR_COUNTER_ADVICES},
                        {SubscriptionType.COUNTER_ADVICES, SubscriptionListType.OWNER, Arrays.asList(1,2,3), SUBSCRIPTION_COUNTER_IDS_ONLY_FOR_LIST},
                        {SubscriptionType.API_NEWS, SubscriptionListType.LIST, Arrays.asList(1, 2, 3), SUBSCRIPTION_LIST_ONLY_FOR_COUNTER_ADVICES},
                        {SubscriptionType.OTHER_OFFERS, SubscriptionListType.OWNER, Collections.emptyList(), SUBSCRIPTION_LIST_ONLY_FOR_COUNTER_ADVICES},
                        {SubscriptionType.PROMO, SubscriptionListType.EDIT, Collections.emptyList(), SUBSCRIPTION_LIST_ONLY_FOR_COUNTER_ADVICES}
                }
        );
    }


    @Before
    public void setup() {
        this.lock = USER.onManagementSteps().onSubscriptionsSteps().getLock();
        USER.onManagementSteps().onSubscriptionsSteps().addClearUserWithDeleteBefore(email);
    }

    @Test
    public void checkSubscription() {
        USER.onManagementSteps().onSubscriptionsSteps().changeSubscriptionAndExpectError(subscriptionType, true,
                subscriptionListType, counterIds, error);
    }

    @After
    public void teardown() {
        lock.ifPresent(ILock::unlock);
    }
}
