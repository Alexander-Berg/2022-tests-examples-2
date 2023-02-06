package ru.yandex.autotests.metrika.tests.ft.management.counter.filters;

import org.junit.Before;
import ru.yandex.autotests.metrika.data.parameters.management.v1.Field;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.filter.FilterAttribute;
import ru.yandex.metrika.api.management.client.filter.FilterE;
import ru.yandex.metrika.api.management.client.filter.FilterType;

import java.util.Arrays;

import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterWithFilters;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getFilter;

public abstract class DefaultCounterWithFilterTest {

    protected UserSteps user;
    protected CounterFull counter;
    protected CounterFull addedCounter;
    protected Long counterId;
    protected FilterE expectedFilter;
    protected FilterE resultFilter;

    @Before
    public void before() {
        user = new UserSteps();
        counter = getCounterWithFilters(
                Arrays.asList(
                        getFilter()
                                .withAttr(getAttribute())
                                .withType(getType())
                                .withValue(getValue())));

        user.onManagementSteps().onCountersSteps().deleteAllCountersWithName(counter.getName());
        addedCounter = user.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(counter, Field.FILTERS);
        counterId = addedCounter.getId();
        resultFilter = addedCounter.getFilters().get(0);
        expectedFilter = counter.getFilters().get(0);
    }

    protected abstract String getValue();

    protected abstract FilterType getType();

    protected abstract FilterAttribute getAttribute();

}
