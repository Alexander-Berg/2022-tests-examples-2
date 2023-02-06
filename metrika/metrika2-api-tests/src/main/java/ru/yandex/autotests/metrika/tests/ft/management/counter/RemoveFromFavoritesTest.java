package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by vananos on 03.08.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчик: проверка исключения счетчика из избранных")
@RunWith(Parameterized.class)
public class RemoveFromFavoritesTest {

    private UserSteps user;
    private CounterFull counter;
    private long counterId;

    @Parameter
    public User userParam;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray(SIMPLE_USER),
                toArray(SIMPLE_USER2_EMAIL),
                toArray(USER_WITH_PHONE_LOGIN),
                toArray(USER_WITH_PHONE_ONLY_LOGIN),
                toArray(SIMPLE_USER_PDD));
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(userParam);
        counter = getDefaultCounter();
        counterId = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter).getId();

        user.onManagementSteps().onCountersSteps().editCounter(counterId, counter.withFavorite(1L));
    }

    @Test
    public void counterShouldNotBeFavorite() {
        user.onManagementSteps().onCountersSteps().editCounter(counterId, counter.withFavorite(0L));
        long favorite = user.onManagementSteps().onCountersSteps().getCounterInfo(counterId).getFavorite();

        assertThat("счетчик не в избранных", favorite, equalTo(0L));
    }

    @After
    public void tearDown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
