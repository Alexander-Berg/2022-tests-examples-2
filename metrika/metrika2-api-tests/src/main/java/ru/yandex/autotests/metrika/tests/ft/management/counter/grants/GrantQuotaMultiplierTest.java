package ru.yandex.autotests.metrika.tests.ft.management.counter.grants;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка размера множителя квот на гранты счетчика")
@RunWith(Parameterized.class)
public class GrantQuotaMultiplierTest {

    private static final Counter COUNTER = Counters.TEST_COUNTER_LIMITS;
    private static final Counter SECOND_COUNTER = Counters.TEST_COUNTER;

    private final User OWNER = Users.SIMPLE_USER;

    private UserSteps owner = new UserSteps().withUser(OWNER);

    private Long counterId;

    @Parameterized.Parameter(0)
    public double expectedMultiplier;

    @Parameterized.Parameter(1)
    public Counter currentCounter;

    @Parameterized.Parameters(name = "Счетчик {1}, у которого множитель = {0}")
    public static Collection<Object[]> createParameters() {
        return of(
                toArray(2.0, COUNTER),
                toArray(1.0, SECOND_COUNTER)
        );
    }

    @Before
    public void setup() {
        counterId = currentCounter.getId();
    }

    @Test
    public void check() {
        double actualMultiplier = owner.onManagementSteps().onQuotaMultiplierSteps().getGrantQuotaMultiplier(counterId);

        TestSteps.assertThat(
                String.format("у счетчика с номером %d, размер множителя на гранты должно равняться к %.2f", counterId, expectedMultiplier),
                actualMultiplier,
                beanEquivalent(expectedMultiplier)
        );
    }
}
