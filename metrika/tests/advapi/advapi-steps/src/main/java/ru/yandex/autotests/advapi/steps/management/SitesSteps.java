package ru.yandex.autotests.advapi.steps.management;

import ru.yandex.advapi.V1ManagementSitesGETSchema;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

public class SitesSteps extends BaseAdvApiSteps {

    public SitesSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить площадки")
    public V1ManagementSitesGETSchema getSitesAndExpectSuccess(IFormParameters... parameters) {
        return getAndExpectSuccess(V1ManagementSitesGETSchema.class, "/v1/management/sites", parameters);
    }

    @Step("Получить площадки и ожидать ошибки {0}")
    public V1ManagementSitesGETSchema getSitesAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getAndExpectError(V1ManagementSitesGETSchema.class, "/v1/management/sites", error, parameters);
    }
}
