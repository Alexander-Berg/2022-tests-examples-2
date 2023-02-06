package ru.yandex.autotests.metrika.tests.ft.management.subscriptions;

import java.util.Collection;
import java.util.Optional;

import com.hazelcast.core.ILock;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.errors.CommonError.EMAIL_NOT_BE_EMPTY;
import static ru.yandex.autotests.metrika.errors.CommonError.INCORRECT_EMAIL;

@Stories(Requirements.Story.Management.SUBSCRIPTION)
@Title("Проверка включения подписки для пользователя - негативные")
@RunWith(Parameterized.class)
public class AddSubscriptionUserNegativeTest {

    private static final UserSteps USER = new UserSteps().withUser(Users.SIMPLE_USER);
    private Optional<ILock> lock;

    @Parameterized.Parameter
    public String email;

    @Parameterized.Parameter(1)
    public IExpectedError expectedError;

    @Parameterized.Parameters(name = "Email: {0}")
    public static Collection<Object[]> createParameters() {
        return asList(
                new Object[][]{
                        {"test-test.ru", INCORRECT_EMAIL},
                        {"test@yandex.u", INCORRECT_EMAIL},
                        {"", EMAIL_NOT_BE_EMPTY}
                }
        );
    }

    @Before
    public void setup() {
        this.lock = USER.onManagementSteps().onSubscriptionsSteps().getLock();
        USER.onManagementSteps().onSubscriptionsSteps().deleteUserSilent();
    }

    @Test
    public void validate() {
        USER.onManagementSteps().onSubscriptionsSteps().addUserAndExpectError(expectedError, email, Users.SIMPLE_USER.get(User.UID));
    }

    @After
    public void teardown() {
        lock.ifPresent(ILock::unlock);
    }
}
