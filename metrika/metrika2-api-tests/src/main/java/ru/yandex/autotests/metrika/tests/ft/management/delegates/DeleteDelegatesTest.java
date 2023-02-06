package ru.yandex.autotests.metrika.tests.ft.management.delegates;

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
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATE;

/**
 * Created by sourx on 04.02.2016.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.DELEGATE)
@Title("Удаление представителя")
public class DeleteDelegatesTest {
    private final User DELEGATE = USER_DELEGATE;
    private final User OWNER = Users.USER_DELEGATOR4;

    private UserSteps userOwner;
    private DelegateE expectedDelegate;

    @Before
    public void setup() {
        expectedDelegate = new DelegateE().withUserLogin(DELEGATE.get(LOGIN)).withComment("Test comment");

        userOwner = new UserSteps().withUser(OWNER);
        userOwner.onManagementSteps().onDelegatesSteps().addDelegateAndExpectSuccess(expectedDelegate);

        List<DelegateE> actualDelegates = userOwner.onManagementSteps().onDelegatesSteps().getDelegatesAndExpectSuccess();

        assumeThat("в списке представителей содержится объект эквивалентный добавленному представителю",
                actualDelegates,
                hasItem(beanEquivalent(expectedDelegate)));

        userOwner.onManagementSteps().onDelegatesSteps().deleteDelegateAndExpectSuccess(DELEGATE.get(LOGIN));
    }

    @Test
    @Title("Удаление представителя")
    public void checkDeletedDelegate() {
        List<DelegateE> actualDelegates = userOwner.onManagementSteps().onDelegatesSteps().getDelegatesAndExpectSuccess();

        assertThat("в списке представителей не содержится объект эквивалентный удаленному представителю",
                actualDelegates,
                not(hasItem(beanEquivalent(expectedDelegate))));
    }
}
