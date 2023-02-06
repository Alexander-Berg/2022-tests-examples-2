package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.hamcrest.Matcher;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.management.v1.counters.enums.CounterSortEnum;
import ru.yandex.autotests.metrika.data.parameters.management.v1.AvailableCountersParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterBrief;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.metrika.data.common.users.Users.USER_FOR_COUNTER_LIST;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.Utils.getEnumListWithNull;

/**
 * Created by proxeter on 24.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка получения списка доступных счетчиков c сортировкой")
@RunWith(Parameterized.class)
public class CountersSortListTest {
    private static final UserSteps user = new UserSteps().withUser(USER_FOR_COUNTER_LIST);
    private static List<Long> counterIds = new ArrayList<>();

    private static final List<Integer> PER_PAGE_VALUES = asList(0, 1, null);
    private static final Integer COUNTERS_NUMBER = 3;
    private static final List<Boolean> REVERSE_VALUES = asList(Boolean.TRUE, Boolean.FALSE, null);

    @Parameterized.Parameter(0)
    public CounterSortEnum sort;

    @Parameterized.Parameter(1)
    public Boolean reverse;

    @Parameterized.Parameter(2)
    public Integer perPage;

    @Parameterized.Parameters(name = "sort: {0}; reverse: {1}; per_page: {2}")
    public static Collection<Object[]> createParameters() {
        ArrayList<Object[]> parameters = new ArrayList<>();

        for (CounterSortEnum counterSortEnum : getEnumListWithNull(CounterSortEnum.class)) {
            for (Boolean reverseValue : REVERSE_VALUES) {
                for (Integer perPageValue : PER_PAGE_VALUES) {
                    parameters.add(toArray(counterSortEnum, reverseValue, perPageValue));
                }
            }
        }

        return parameters;
    }

    private AvailableCountersParameters parameters;

    @BeforeClass
    public static void init() {
        user.onManagementSteps().onCountersSteps().deleteAllCounters();
        for (int i = 0; i < COUNTERS_NUMBER; i++) {
            counterIds.add(user.onManagementSteps().onCountersSteps()
                    .addCounterAndExpectSuccess(getDefaultCounter()).getId());
        }
    }

    @Before
    public void setup() {
        parameters = new AvailableCountersParameters()
                .withSort(sort)
                .withReverse(reverse)
                .withPerPage(perPage);
    }

    @Test
    public void availableCountersTest() {
        List<CounterBrief> counters = user.onManagementSteps().onCountersSteps()
                .getAvailableCountersAndExpectSuccess(parameters);

        assertThat("Количество счетчиков в списке совпадает с ожидаемым", counters,
                iterableWithSize(getSizeMatcher()));
    }

    @AfterClass
    public static void cleanup() {
        for (Long counterId : counterIds) {
            user.onManagementSteps().onCountersSteps().deleteCounterAndIgnoreStatus(counterId);
        }
    }

    private Matcher<Integer> getSizeMatcher() {
        return perPage != null
                ? equalTo(perPage)
                : equalTo(COUNTERS_NUMBER);

    }

}
