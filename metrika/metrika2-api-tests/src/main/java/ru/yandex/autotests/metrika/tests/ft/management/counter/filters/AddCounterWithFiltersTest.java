package ru.yandex.autotests.metrika.tests.ft.management.counter.filters;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.metrika.api.management.client.filter.FilterAttribute;
import ru.yandex.metrika.api.management.client.filter.FilterType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by proxeter on 24.07.2014.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка добавления счетчика с фильтрами IP-адресов")
@RunWith(Parameterized.class)
public class AddCounterWithFiltersTest extends DefaultCounterWithFilterTest {

    @Parameterized.Parameter(0)
    public String value;

    @Parameterized.Parameter(1)
    public String startIp;

    @Parameterized.Parameter(2)
    public String endIp;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(toArray("2.57.1.250", "::FFFF:2.57.1.250", "::FFFF:2.57.1.250"))
                .add(toArray("2.57.1.250-2.57.1.252", "::FFFF:2.57.1.250", "::FFFF:2.57.1.252"))
                .add(toArray("2.57.1.250/20", "::FFFF:2.57.0.0", "::FFFF:2.57.15.255"))
                .add(toArray("2.57.1.*", "::FFFF:2.57.1.0", "::FFFF:2.57.1.255"))
                .add(toArray("2601:14a:4602:5190:b950:7a9c:da66:26dc", "2601:14a:4602:5190:b950:7a9c:da66:26dc",
                        "2601:14a:4602:5190:b950:7a9c:da66:26dc"))
                .add(toArray("2601:14a:4602:5190:b950:7a9c:0:26-2601:14a:4602:5190:b950:7a9c::31",
                        "2601:14a:4602:5190:b950:7a9c:0:26", "2601:14a:4602:5190:b950:7a9c:0:31"))
                .add(toArray("2001:db8:abcd:0012::0/64", "2001:db8:abcd:12:0:0:0:0",
                        "2001:db8:abcd:12:ffff:ffff:ffff:ffff"))
                .build();
    }

    @Test
    public void filterTest() {
        assertThat("созданный фильтр имеет заданные атрибуты", resultFilter, beanEquivalent(expectedFilter));
    }

    @Test
    public void filterStartIpTest() {
        assertThat("поле start_ip сохранилось верно", resultFilter.getStartIp(), equalTo(startIp));
    }

    @Test
    public void filterEndIpTest() {
        assertThat("поле end_ip сохранилось верно", resultFilter.getEndIp(), equalTo(endIp));
    }

    @After
    public void after() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

    @Override
    public String getValue() {
        return value;
    }

    @Override
    protected FilterAttribute getAttribute() {
        return FilterAttribute.CLIENT_IP;
    }

    @Override
    protected FilterType getType() {
        return FilterType.INTERVAL;
    }
}
