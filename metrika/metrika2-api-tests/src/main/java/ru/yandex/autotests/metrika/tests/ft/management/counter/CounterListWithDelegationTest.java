package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItem;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATE_PERMANENT;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_DELEGATOR;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.errors.ManagementError.ACCESS_DENIED;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 29.12.2014.
 * <p/>
 * https://st.yandex-team.ru/TESTIRT-3800
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка получения списка доступных счетчиков через представительский доступ")
public class CounterListWithDelegationTest {

    private static final User DELEGATOR = USER_DELEGATOR;
    private static final User DELEGATE = USER_DELEGATE_PERMANENT;

    /**
     * первый пользователь - кто делегирует
     */
    private UserSteps user;

    /**
     * второй пользователь - кому делегирует - делегат
     */
    private UserSteps userDelegate;

    /**
     * счетчик делегированного пользователя
     */
    private Long counterDelegatedId;

    /**
     * счетчик пользователя - делегата
     */
    private Long counterId;

    @Before
    public void setup() {

        user = new UserSteps().withUser(DELEGATOR);
        userDelegate = new UserSteps().withUser(DELEGATE);

        //создаем по одному счетчику
        counterDelegatedId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();

        counterId = userDelegate.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter()).getId();
    }

    @Test
    public void availableCountersWithDelegationTest() {
        //запрос с параметром ulogin
        List<CounterBrief> availableCounters =
                userDelegate.onManagementSteps().onCountersSteps()
                        .getAvailableCountersAndExpectSuccess(ulogin(DELEGATOR.get(LOGIN)));

        List<Long> availableCounterIds = with(availableCounters).extract(on(CounterBrief.class).getId());

        //проверим, что в списке есть счетчик от другого пользователя

        assertThat("в списке счетчиков присутствует счетчик делегировавшего пользователя", availableCounterIds,
                hasItem(equalTo(counterDelegatedId)));
    }

    @Test
    public void availableCountersWithoutDelegationTest() {
        //запрос с параметром ulogin
        user.onManagementSteps().onCountersSteps()
                .getAvailableCountersAndExpectError(ACCESS_DENIED, ulogin(DELEGATE.get(LOGIN)));
    }

    @After
    public void teardown() {
        //удаляем счетчики
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterDelegatedId);
        userDelegate.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
