package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.revenue;

import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.managers.Currency;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.Arrays.asList;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;

@Features({Requirements.Feature.Management.REVENUE})
@Stories({
        Requirements.Story.Revenue.LIST_REVENUE_CURRENCIES
})
@Title("Валюты revenue-отчёта")
public class RevenueReportCurrenciesTest {

    private static final List<String> EXPECTED_REVENUE_CURRENCIES = asList("EUR", "RUB", "USD");

    private static final UserSteps user = UserSteps.onTesting(Users.SIMPLE_USER);

    @Test
    public void checkRevenueReportCurrencies() {
        List<String> currencies = user.onRevenueCurrenciesSteps().getRevenueReportCurrencies().stream()
                .map(Currency::getCode)
                .sorted()
                .collect(toList());

        assertThat("список валют revenue-отчёта эквивалентен ожидаемому", currencies,
                equivalentTo(EXPECTED_REVENUE_CURRENCIES));
    }
}
