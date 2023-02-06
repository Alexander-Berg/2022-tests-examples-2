package ru.yandex.autotests.metrika.tests.ft.management.counter;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.managers.Currency;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.emptyCollectionOf;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.requestDomain;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by sourx on 12.07.16.
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Проверка валюты по умолчанию в счетчике")
@RunWith(Parameterized.class)
public class CounterCurrencyTest {
    private final static Long RUB = 643L;
    private final static Long USD = 840L;
    private final static Long UAH = 980L;
    private final static Long KZT = 398L;
    private final static Long BYN = 933L;
    private final static Long TRY = 949L;

    private UserSteps user;
    private Long counterId;

    @Parameterized.Parameter()
    public static String requestDomain;

    @Parameterized.Parameter(1)
    public static Long expectedCurrency;

    @Parameterized.Parameters(name = "Домен: {0}, валюта: {1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                        {"ru", RUB},
                        {"com", USD},
                        {"ua", UAH},
                        {"kz", KZT},
                        {"by", BYN},
                        {"tr", TRY},
                        {"de", RUB},
                        {null, RUB}
                }
        );
    }

    @Before
    public void before() {
        user = new UserSteps();

        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter(), requestDomain(requestDomain)).getId();
    }

    @Test
    public void checkCounterCurrency() {
        Long actualCurrency = user.onManagementSteps().onCountersSteps().getCounterInfo(counterId).getCurrency();
        assertThat("валюта совпадает с ожидаемой", actualCurrency, equalTo(expectedCurrency));
    }

    @After
    public void after() {
        user.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
