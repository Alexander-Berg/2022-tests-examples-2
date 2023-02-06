package ru.yandex.autotests.metrika.appmetrica.steps;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1RevenueCurrencyGETSchema;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.managers.Currency;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class RevenueCurrenciesSteps extends AppMetricaBaseSteps {

    public RevenueCurrenciesSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список групп для приложения {0}")
    @ParallelExecution(ALLOW)
    public List<Currency> getRevenueReportCurrencies() {
        return doGetGroupList();
    }

    private List<Currency> doGetGroupList() {
        ManagementV1RevenueCurrencyGETSchema result = get(
                ManagementV1RevenueCurrencyGETSchema.class,
                "/management/v1/revenue/currency");

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getCurrencies();
    }

}
