package ru.yandex.autotests.metrika.tests.ft.management.delegates;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.DelegateE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATE;

/**
 * Created by sourx on 05.02.2016.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.DELEGATE)
@Title("Список представителей")
public class DelegatesListTest {
    private final User DELEGATE = USER_DELEGATE;
    private final User OWNER = Users.USER_DELEGATOR3;

    private UserSteps userOwner;

    @Before
    public void setup() {
        userOwner = new UserSteps().withUser(OWNER);
        userOwner.onManagementSteps().onDelegatesSteps()
                .addDelegateAndExpectSuccess(new DelegateE().withUserLogin(DELEGATE.get(LOGIN))
                        .withComment("Test comment"));
    }

    @Test
    @Title("Добавленный пользователь в списке представителей")
    public void checkAddedUser() {
        DelegateE expectedDelegate = new DelegateE().withUserLogin(DELEGATE.get(LOGIN)).withComment("Test comment");
        List<DelegateE> actualDelegates = userOwner.onManagementSteps()
                .onDelegatesSteps().getDelegatesAndExpectSuccess();

        assertThat("в списке представителей содержится объект эквивалентный добавленному представителю",
                actualDelegates,
                hasItem(beanEquivalent(expectedDelegate)));
    }

    @After
    public void teardown() {
        userOwner.onManagementSteps().onDelegatesSteps().deleteDelegateAndExpectSuccess(DELEGATE.get(LOGIN));
    }
}
