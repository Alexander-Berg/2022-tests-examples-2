package ru.yandex.autotests.metrika.tests.ft.management.delegates;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.DelegateE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATE;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterName;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterSite;

/**
 * Created by sourx on 04.02.2016.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.DELEGATE)
@Title("Добавление представителя")
public class AddDelegatesTest {
    private final User DELEGATE = USER_DELEGATE;
    private final User OWNER = Users.USER_DELEGATOR2;

    private UserSteps userOwner;
    private UserSteps userDelegate;
    private Long counterId;

    @Before
    public void setup() {
        userOwner = new UserSteps().withUser(OWNER);
        userDelegate = new UserSteps().withUser(DELEGATE);

        userOwner.onManagementSteps().onDelegatesSteps().addDelegateAndExpectSuccess(new DelegateE()
                .withUserLogin(DELEGATE.get(LOGIN)).withComment("Test comment"));
        counterId = userOwner.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(new CounterFull()
                        .withSite(getCounterSite())).getId();
    }

    @Test
    @Title("Информация о счетчике доступна представителю")
    public void checkDelegatorCounterInfo() {
        CounterFull expectedCounter = userDelegate.onManagementSteps().onCountersSteps().getCounterInfo(counterId);
        CounterFull actualCounter = userOwner.onManagementSteps().onCountersSteps().getCounterInfo(counterId);

        assertThat("данные счетчика, полученные представителем эквивалентны данным, полученным владельцем",
                actualCounter,
                beanEquivalent(expectedCounter));
    }

    @Test
    @Title("Редактирование счетчика представителем")
    public void editDelegatorCounter() {
        CounterFull expectedCounter = userDelegate.onManagementSteps()
                .onCountersSteps().editCounter(counterId, new CounterFull()
                        .withName(getCounterName()));
        CounterFull actualCounter = userOwner.onManagementSteps().onCountersSteps().getCounterInfo(counterId);

        assertThat("счетчик отредактирован представителем",
                actualCounter,
                beanEquivalent(expectedCounter));
    }

    @After
    public void teardown() {
        userOwner.onManagementSteps().onDelegatesSteps().deleteDelegateAndExpectSuccess(DELEGATE.get(LOGIN));
        userOwner.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
