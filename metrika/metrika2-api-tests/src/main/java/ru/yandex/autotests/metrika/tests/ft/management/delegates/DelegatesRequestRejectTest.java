package ru.yandex.autotests.metrika.tests.ft.management.delegates;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.DelegateE;
import ru.yandex.metrika.api.management.client.external.DelegateRequestE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATOR2;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by sourx on 15.02.2016.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.DELEGATE)
@Title("Запрос представительства (отклонение)")
public class DelegatesRequestRejectTest {
    private final User OWNER = USER_DELEGATOR2;
    private final User DELEGATE = Users.SIMPLE_USER_WITH_MONEY_1;

    private UserSteps userOwner;
    private UserSteps userDelegate;

    private DelegateE expectedDelegate;

    @Before
    public void setup() {
        userOwner = new UserSteps().withUser(OWNER);
        userDelegate = new UserSteps().withUser(DELEGATE);

        expectedDelegate = new DelegateE().withUserLogin(DELEGATE.get(LOGIN));
        List<DelegateE> actualDelegates = userOwner.onManagementSteps()
                .onDelegatesSteps().getDelegatesAndExpectSuccess();

        assumeThat("у пользователя нет представителей", actualDelegates, not(hasItem(expectedDelegate)));

        userDelegate.onManagementSteps().onDelegatesSteps()
                .requestDelegateAndExpectSuccess(OWNER.get(LOGIN), DELEGATE.get(LOGIN));
    }

    @Test
    @Title("Отклонение запроса на представительство")
    public void rejectDelegate() {
        DelegateRequestE expectedDelegateRequest = new DelegateRequestE().withUserLogin(DELEGATE.get(LOGIN));
        List<DelegateRequestE> actualDelegateRequests = userOwner.onManagementSteps()
                .onDelegatesSteps().getDelegateRequests();

        assumeThat("в запросах на представительство присутствует пользователь", actualDelegateRequests,
                hasItem(expectedDelegateRequest));

        userOwner.onManagementSteps().onDelegatesSteps().rejectDelegateRequestAndExpectSuccess(DELEGATE.get(LOGIN));

        List<DelegateE> actualDelegates = userOwner.onManagementSteps()
                .onDelegatesSteps().getDelegatesAndExpectSuccess();

        assertThat("запрос отклонен, пользователь не добавился",
                actualDelegates,
                not(hasItem(beanEquivalent(expectedDelegate))));
    }
}
