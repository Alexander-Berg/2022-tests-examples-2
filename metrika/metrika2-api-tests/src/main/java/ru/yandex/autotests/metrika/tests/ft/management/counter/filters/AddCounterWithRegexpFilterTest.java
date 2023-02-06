package ru.yandex.autotests.metrika.tests.ft.management.counter.filters;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.api.management.client.filter.FilterAttribute;
import ru.yandex.metrika.api.management.client.filter.FilterType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка добавления счетчика с фильтрами регулярных выражений")
@RunWith(Parameterized.class)
public class AddCounterWithRegexpFilterTest extends DefaultCounterWithFilterTest {

    @Parameterized.Parameter(0)
    public FilterAttribute attribute;

    @Parameterized.Parameter(1)
    public FilterType type;

    @Parameterized.Parameter(2)
    public String value;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(FilterAttribute.TITLE, FilterAttribute.URL)
                .vectorValues(ImmutableList.of(FilterType.REGEXP, "^[.]+[a-c]$"))
                .build();
    }

    @Test
    public void testValidRegexpFilter() {
        assertThat("созданный фильтр имеет заданные атрибуты", resultFilter, beanEquivalent(expectedFilter));
    }

    @After
    public void after() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
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
