package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterSource;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;

import static org.junit.Assert.assertEquals;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPER_USER;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Fields.all;
import static ru.yandex.autotests.metrika.matchers.CounterMatchers.beanEquivalentIgnoringFeatures;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getTurbodirectCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчик: проверка добавления счетчика Турбо-директ")
@RunWith(Parameterized.class)
public class AddTurbodirectCounterTest {
    private UserSteps user;
    private Long counterId;
    private CounterFull counter;
    private CounterFull addedCounter;

    @Parameterized.Parameter(0)
    public Boolean autogoalsEnabled;

    @Before
    public void setup() {
        user = new UserSteps().withUser(SUPER_USER);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(new Object[][]{
                {true},
                {null}
        });
    }

    @Test
    public void test() {
        counter = getTurbodirectCounter().withAutogoalsEnabled(autogoalsEnabled);

        addedCounter = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(counter, all());

        counterId = addedCounter.getId();

        assertThat("добавленный счетчик должен быть эквивалентен добавляемому счетчику кроме поля autogoals_enabled, которая всегда должна быть равна к false", addedCounter,
                beanEquivalentIgnoringFeatures(counter.withAutogoalsEnabled(false)));
    }

    @After
    public void tearDown() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
