package ru.yandex.autotests.metrika.tests.b2b.management.counters;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.management.v1.counters.enums.CounterSortEnum;
import ru.yandex.autotests.metrika.data.parameters.management.v1.AvailableCountersParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints.only;
import static ru.yandex.autotests.metrika.data.common.users.Users.METRIKA_TEST_COUNTERS;

/**
 * Created by sourx on 30.03.17.
 */
@Features({Requirements.Feature.MANAGEMENT, Requirements.Feature.DATA})
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка сортировки списка счетчиков")
@RunWith(Parameterized.class)
public class B2bCounterListSortTest {

    private static final List<Boolean> REVERSE_VALUES = asList(Boolean.TRUE, Boolean.FALSE, null);

    private UserSteps userOnTest = new UserSteps().withUser(METRIKA_TEST_COUNTERS);
    private UserSteps userOnRef = new UserSteps().withUser(METRIKA_TEST_COUNTERS).useReference();
    private List<CounterBrief> testList;
    private List<CounterBrief> refList;

    @Parameterized.Parameter(0)
    public CounterSortEnum sort;

    @Parameterized.Parameter(1)
    public Boolean reverse;

    @Parameterized.Parameters(name = "Тип сортировки: {0}, обратная: {1}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(CounterSortEnum.values())
                .values(REVERSE_VALUES)
                .build();
    }

    @Before
    public void setup() {
        AvailableCountersParameters parameters = new AvailableCountersParameters()
                .withSort(sort)
                .withReverse(reverse);

        testList = userOnTest.onManagementSteps().onCountersSteps().getAvailableCountersAndExpectSuccess(parameters);
        refList = userOnRef.onManagementSteps().onCountersSteps().getAvailableCountersAndExpectSuccess(parameters);
    }

    @Test
    public void counterListsShouldBeTheSame() {
        assertThat("списки отсортированы одинаково", testList,
                beanEquivalent(refList).fields(only("counters/id")));
    }
}
