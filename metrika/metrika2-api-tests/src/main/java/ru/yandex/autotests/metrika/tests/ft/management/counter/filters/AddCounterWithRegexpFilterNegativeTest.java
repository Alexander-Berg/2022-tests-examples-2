package ru.yandex.autotests.metrika.tests.ft.management.counter.filters;

import com.google.common.collect.ImmutableList;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.parameters.management.v1.Field;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.filter.FilterAttribute;
import ru.yandex.metrika.api.management.client.filter.FilterType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.hamcrest.Matchers.nullValue;
import static org.hamcrest.core.Is.is;
import static ru.yandex.autotests.metrika.errors.ManagementError.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterWithFilters;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getFilter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка добавления счетчика с фильтрами невалидных регулярных выражений")
@RunWith(Parameterized.class)
public class AddCounterWithRegexpFilterNegativeTest extends DefaultCounterWithFilterTest {
    @Parameterized.Parameter(0)
    public FilterAttribute attribute;

    @Parameterized.Parameter(1)
    public IExpectedError expectedError;

    @Parameterized.Parameter(2)
    public FilterType type;

    @Parameterized.Parameter(3)
    public String value;

    @Before
    @Override
    public void before() {
        user = new UserSteps();
        counter = getCounterWithFilters(
                ImmutableList.of(
                        getFilter()
                                .withAttr(getAttribute())
                                .withType(getType())
                                .withValue(getValue())));

        user.onManagementSteps().onCountersSteps().deleteAllCountersWithName(counter.getName());
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .addAll(CombinatorialBuilder.builder()
                        .values(FilterAttribute.TITLE, FilterAttribute.URL)
                        .vectorValues(ImmutableList.of(INVALID_FIRST_FILTER, FilterType.REGEXP, "06437)Q^#(@*!)#^!8096)#^@*(!)^"))
                        .build())
                .addAll(CombinatorialBuilder.builder()
                        .vectorValues(
                                ImmutableList.of(FilterAttribute.REFERER, INVALID_REFERER_FILTER),
                                ImmutableList.of(FilterAttribute.CLIENT_IP, INVALID_IP_FILTER),
                                ImmutableList.of(FilterAttribute.UNIQ_ID, INVALID_UNIQ_ID_FILTER))
                        .vectorValues(ImmutableList.of(FilterType.REGEXP, "valid filter"))
                        .build())
                .build();
    }

    @Test
    @Title("Добавление счётчика с невалидным фильтром")
    public void testCounterWithInvalidFilter() {
        addedCounter = user.onManagementSteps().onCountersSteps().addCounterAndExpectError(expectedError, counter, Field.FILTERS);
        assertThat("Счётчик не создан", addedCounter, is(nullValue()));
    }

    @Override
    protected String getValue() {
        return value;
    }

    @Override
    protected FilterType getType() {
        return type;
    }

    @Override
    protected FilterAttribute getAttribute() {
        return attribute;
    }
}
