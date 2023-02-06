package ru.yandex.autotests.metrika.tests.ft.internal;

import java.util.Collection;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static org.junit.Assert.assertEquals;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.PARTNER_TEST_1;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPER_USER;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка признака больших счетчиков")
@RunWith(Parameterized.class)
public class BignessCheckTest {

    private UserSteps user;

    @Parameterized.Parameter(0)
    public Counter counter;

    @Parameterized.Parameter(1)
    public Boolean isBig;

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                        {YANDEX_METRIKA_2_0, true},
                        {PARTNER_TEST_1, false}
                }
        );
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(SUPER_USER);
    }

    @Test
    @Title("Проверка размера счетчика")
    public void checkBigness() {
        assertEquals("полученное значение размера счетчика совпадает с ожидаемым",
        user.onManagementSteps().onCountersSteps().getCounterBignessStatus(counter.getId()), isBig);
    }

}
