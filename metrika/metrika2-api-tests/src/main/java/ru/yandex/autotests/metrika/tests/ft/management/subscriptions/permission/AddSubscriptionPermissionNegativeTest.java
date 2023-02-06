package ru.yandex.autotests.metrika.tests.ft.management.subscriptions.permission;

import java.util.Collection;
import java.util.Collections;
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
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPER_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPPORT;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATE_PERMANENT;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.SUBSCRIPTION)
@Title("Проверка прав включения подписки для пользователя(негативные)")
@RunWith(Parameterized.class)
public class AddSubscriptionPermissionNegativeTest {
    private static final UserSteps USER = new UserSteps().withUser(Users.USER_DELEGATOR);

    private static final User OTHER = Users.SIMPLE_USER3;
    private static final User MANAGER = Users.MANAGER;
    private static final User DIRECT = Users.MANAGER_DIRECT;
    private static final User YAMANAGER = Users.YAMANAGER;
    private static final User DELEGATE = USER_DELEGATE_PERMANENT;


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
                        {"иной пользователь", OTHER},
                        {"представитель", DELEGATE},
                        {"менеджер", MANAGER},
                        {"менеджер Директа", DIRECT},
                        {"яндекс менеджер", YAMANAGER}
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
        new UserSteps().withUser(currentUser).onManagementSteps().onSubscriptionsSteps().changeSubscriptionAndExpectError(Users.SIMPLE_USER.get(User.UID), SubscriptionType.PROMO, true, SubscriptionListType.ALL, Collections.emptyList(), ACCESS_DENIED);
    }

    @After
    public void teardown() {
        lock.ifPresent(ILock::unlock);
    }
}
