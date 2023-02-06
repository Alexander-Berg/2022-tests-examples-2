package ru.yandex.autotests.metrika.tests.ft.management.counter.boundary;

import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.filter.FilterE;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.List;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.Field.FILTERS;
import static ru.yandex.autotests.metrika.errors.ManagementError.FILTERS_LIMIT;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getFilter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getFilters;

/**
 * Created by okunev on 09.09.2015.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Тест заданного ограничения на количество фильтров в счетчике")
public class CounterMaxFiltersCustomValueTest {

    private static final User USER = SIMPLE_USER;
    private static final Counter COUNTER = Counters.TEST_COUNTER_LIMITS;
    private static final int CUSTOM_MAX_FILTERS = 40;

    private static UserSteps user;

    private List<FilterE> addedFilters = new ArrayList<>();

    @BeforeClass
    public static void init() {
        user = new UserSteps().withUser(USER);
    }

    @Before
    public void setup() {
        CounterFull counterInfo = user.onManagementSteps().onCountersSteps()
                .getCounterInfo(COUNTER.get(ID), FILTERS);

        int currentFilters = counterInfo.getFilters().size();

        List<FilterE> filters = getFilters(CUSTOM_MAX_FILTERS - currentFilters);

        addedFilters = user.onManagementSteps().onFiltersSteps().addFilters(COUNTER.get(ID), filters);
    }

    @Test
    public void createMoreThanMaximumNumberOfFilters() {
        user.onManagementSteps().onFiltersSteps()
                .addFilterAndExpectError(FILTERS_LIMIT, COUNTER.get(ID), getFilter());
    }

    @After
    public void teardown() {
        user.onManagementSteps().onFiltersSteps().deleteFilters(COUNTER.get(ID), addedFilters);
    }

}
