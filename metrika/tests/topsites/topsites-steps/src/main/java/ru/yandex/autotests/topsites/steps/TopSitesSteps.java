package ru.yandex.autotests.topsites.steps;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.autotests.metrika.commons.schemas.CsvResponseSchema;
import ru.yandex.autotests.metrika.commons.schemas.XlsxResponseSchema;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.topsites.*;

import java.net.URL;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class TopSitesSteps extends HttpClientLiteFacade {

    public TopSitesSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить отчет топ v2")
    public GlobalTopsitesReport2GETSchema getReport2(IFormParameters... parameters) {
        return getAndExpectSuccess(GlobalTopsitesReport2GETSchema.class, "/global/topsites/report2", parameters);
    }

    @Step("Получить отчет топ v2 в формате csv")
    public CsvResponseSchema getReport2Csv(IFormParameters... parameters) {
        return getAndExpectSuccess(CsvResponseSchema.class, "/global/topsites/report2.csv", parameters);
    }

    @Step("Получить отчет топ v2 в формате xlsx")
    public XlsxResponseSchema getReport2Xlsx(IFormParameters... parameters) {
        return getAndExpectSuccess(XlsxResponseSchema.class, "/global/topsites/report2.xlsx", parameters);
    }

    @Step("Получить доступные периоды отчетов v2")
    public GlobalTopsitesReport2PeriodsAvailableGETSchema getPeriodsAvailable2(IFormParameters... parameters) {
        return getAndExpectSuccess(GlobalTopsitesReport2PeriodsAvailableGETSchema.class, "/global/topsites/report2/periods_available", parameters);
    }


    private <T> T getAndExpectSuccess(Class<T> responseTypeClass, String path, IFormParameters... parameterses) {
        T response = get(responseTypeClass, path, parameterses);

        //noinspection unchecked
        TestSteps.assumeThat(SUCCESS_MESSAGE, response, expectSuccess());

        return response;
    }
}
