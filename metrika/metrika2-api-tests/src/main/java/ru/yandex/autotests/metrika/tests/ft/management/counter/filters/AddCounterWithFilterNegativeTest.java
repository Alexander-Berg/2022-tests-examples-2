package ru.yandex.autotests.metrika.tests.ft.management.counter.filters;

import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.filter.FilterAction;
import ru.yandex.metrika.api.management.client.filter.FilterAttribute;
import ru.yandex.metrika.api.management.client.filter.FilterE;
import ru.yandex.metrika.api.management.client.filter.FilterType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;
import static ru.yandex.autotests.metrika.errors.ManagementError.NOT_ALLOWED_SYMBOLS_IN_FILTER_VALUE;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterWithFilters;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка добавления счетчика с фильтрами IP-адресов (негативные)")
public class AddCounterWithFilterNegativeTest {
    private final UserSteps user = new UserSteps();

    @Test
    public void filterWithNotAllowedSymbolsInValue() {
        CounterFull counter = getCounterWithFilters(singletonList(
                new FilterE()
                        .withAttr(FilterAttribute.URL)
                        .withType(FilterType.EQUAL)
                        .withValue("\uD83D\uDCC5")
                        .withAction(FilterAction.EXCLUDE)
        ));

        user.onManagementSteps().onCountersSteps().addCounterAndExpectError(NOT_ALLOWED_SYMBOLS_IN_FILTER_VALUE, counter);
    }

}
