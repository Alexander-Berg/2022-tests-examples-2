package ru.yandex.autotests.metrika.tests.ft.management.counter;

import java.util.List;

import org.hamcrest.Matcher;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.managers.Currency;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.containsInAnyOrder;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sourx on 12.07.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка валюты в счетчике")
public class CounterCurrency2Test {

    private static final Long counterId = Counters.HOLODILNIKRU.getId();
    private static final Currency RUB = new Currency().withCode("RUB").withId(643L).withName("Российский рубль");
    private static final Currency USD = new Currency().withCode("USD").withId(840L).withName("Доллар США");
    private Matcher<Iterable<? extends Currency>> expectedCurrency = containsInAnyOrder(RUB, USD);

    private UserSteps user;

    @Before
    public void before() {
        user = new UserSteps();
    }

    @Test
    public void checkCounterCurrency() {
        List<Currency> currency = user.onManagementSteps().onCurrencySteps().getCurrency(counterId);
            assertThat("валюта совпадает с ожидаемой", currency, expectedCurrency);
    }

}
