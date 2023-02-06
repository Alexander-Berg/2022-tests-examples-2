package ru.yandex.autotests.metrika.tests.ft.management.subscriptions;

import java.util.Collection;
import java.util.Optional;

import com.hazelcast.core.ILock;
import org.apache.commons.lang3.StringUtils;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionAccountStatus;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionUser;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.errors.CommonError.EMAIL_NOT_BE_EMPTY;
import static ru.yandex.autotests.metrika.errors.CommonError.INCORRECT_EMAIL;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Stories(Requirements.Story.Management.SUBSCRIPTION)
@Title("Проверка включения подписки для пользователя")
@RunWith(Parameterized.class)
public class AddSubscriptionUserTest {

    private static final UserSteps USER = new UserSteps().withUser(Users.SIMPLE_USER);
    private Optional<ILock> lock;

    @Parameterized.Parameter
    public String email = " test@test.ru";

    @Parameterized.Parameters(name = "Email: {0}")
    public static Collection<Object[]> createParameters() {
        return asList(
                new Object[][]{
                        {"test@test.ru"},
                        {" test1@yandex.ru "}
                }
        );
    }


    @Before
    public void setup() {
        this.lock = USER.onManagementSteps().onSubscriptionsSteps().getLock();
        USER.onManagementSteps().onSubscriptionsSteps().deleteUserSilent();

        USER.onManagementSteps().onSubscriptionsSteps().addUser(email);
    }

    @Test
    public void checkSubscribed() {
        final SubscriptionUser user = USER.onManagementSteps().onSubscriptionsSteps().getUser();
        assertThat("вернулась корректная информация по подписанному пользователю", user, beanEquivalent(new SubscriptionUser()
                .withEmail(StringUtils.trim(email))
                .withLanguage("ru")
                .withStatus(SubscriptionAccountStatus.SUBSCRIBED)
        ));
    }

    @After
    public void teardown() {
        lock.ifPresent(ILock::unlock);
    }
}
