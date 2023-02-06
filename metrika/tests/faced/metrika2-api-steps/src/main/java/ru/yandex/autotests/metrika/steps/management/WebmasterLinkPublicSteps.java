package ru.yandex.autotests.metrika.steps.management;

import org.apache.http.HttpEntity;
import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.autotests.metrika.utils.EmptyHttpEntity;
import ru.yandex.metrika.api.management.client.webmaster.WebmasterLink;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

public class WebmasterLinkPublicSteps extends MetrikaBaseSteps {
    @Step("Получить список привязок для счетчика {0}")
    public List<WebmasterLink> getAllLinksAndExpectSuccess(Long counterId, IFormParameters... parameters) {
        return getAllLinks(counterId, SUCCESS_MESSAGE, expectSuccess(), parameters).getWebmasterLinks();
    }

    private ManagementV1CounterCounterIdWebmasterLinkListGETSchema getAllLinks(Long counterId, String message, Matcher matcher, IFormParameters... parameters) {
        ManagementV1CounterCounterIdWebmasterLinkListGETSchema result =
                executeAsJson(getRequestBuilder(String.format("/management/v1/counter/%s/webmaster_link/list", counterId)).get(parameters))
                        .readResponse(ManagementV1CounterCounterIdWebmasterLinkListGETSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Получить данные привязки для счетчика {0} и домена {1}")
    public WebmasterLink getLinkInfoAndExpectSuccess(Long counterId, String domain, IFormParameters... parameters) {
        return getLinkInfo(counterId, domain, SUCCESS_MESSAGE, expectSuccess(), parameters).getWebmasterLink();
    }

    private ManagementV1CounterCounterIdWebmasterLinkInfoGETSchema getLinkInfo(Long counterId, String domain, String message, Matcher matcher, IFormParameters... parameters) {
        ManagementV1CounterCounterIdWebmasterLinkInfoGETSchema result =
                executeAsJson(getRequestBuilder(String.format("/management/v1/counter/%s/webmaster_link/info", counterId)).get(makeParameters("domain", domain).append(parameters)))
                        .readResponse(ManagementV1CounterCounterIdWebmasterLinkInfoGETSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать привязку для счетчика {0} и домена {1} на стороне метрики")
    public WebmasterLink createLinkAndExpectSuccess(Long counterId, String domain, IFormParameters... parameters) {
        return createLink(counterId, domain, SUCCESS_MESSAGE, expectSuccess(), parameters).getWebmasterLink();
    }

    @Step("Создать привязку для счетчика {0} и домена {1} на стороне метрики и ожидать ошибку {2}")
    public WebmasterLink createLinkAndExpectError(Long counterId, String domain, IExpectedError error, IFormParameters... parameters) {
        return createLink(counterId, domain, ERROR_MESSAGE, expectError(error), parameters).getWebmasterLink();
    }

    private ManagementV1CounterCounterIdWebmasterLinkCreatePOSTSchema createLink(Long counterId, String domain, String message, Matcher matcher, IFormParameters... parameters) {
        ManagementV1CounterCounterIdWebmasterLinkCreatePOSTSchema result =
                executeAsJson(getRequestBuilder(String.format("/management/v1/counter/%s/webmaster_link/create", counterId))
                        .post(new EmptyHttpEntity(), makeParameters("domain", domain).append(parameters))).readResponse(ManagementV1CounterCounterIdWebmasterLinkCreatePOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить привязку для счетчика {0} и домена {1} на стороне метрики")
    public WebmasterLink deleteLinkAndExpectSuccess(Long counterId, String domain, IFormParameters... parameters) {
        return deleteLink(counterId, domain, SUCCESS_MESSAGE, expectSuccess(), parameters).getWebmasterLink();
    }

    @Step("Удалить привязку для счетчика {0} и домена {1} на стороне метрики и ожидать ошибку {2}")
    public WebmasterLink deleteLinkAndExpectError(Long counterId, String domain, IExpectedError error, IFormParameters... parameters) {
        return deleteLink(counterId, domain, ERROR_MESSAGE, expectError(error), parameters).getWebmasterLink();
    }

    @Step("Удалить привязку для счетчика {0} и домена {1} на стороне метрики и игнорировать результат")
    public WebmasterLink deleteLinkAndIgnoreResult(Long counterId, String domain, IFormParameters... parameters) {
        return deleteLink(counterId, domain, ANYTHING_MESSAGE, expectAnything(), parameters).getWebmasterLink();
    }

    private ManagementV1CounterCounterIdWebmasterLinkDeletePOSTSchema deleteLink(Long counterId, String domain, String message, Matcher matcher, IFormParameters... parameters) {
        ManagementV1CounterCounterIdWebmasterLinkDeletePOSTSchema result =
                executeAsJson(getRequestBuilder(String.format("/management/v1/counter/%s/webmaster_link/delete", counterId))
                        .post(new EmptyHttpEntity(), makeParameters("domain", domain).append(parameters))).readResponse(ManagementV1CounterCounterIdWebmasterLinkDeletePOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Подтвердить привязку для счетчика {0} и домена {1} на стороне метрики")
    public WebmasterLink confirmLinkAndExpectSuccess(Long counterId, String domain, IFormParameters... parameters) {
        return confirmLink(counterId, domain, SUCCESS_MESSAGE, expectSuccess(), parameters).getWebmasterLink();
    }

    @Step("Подтвердить привязку для счетчика {0} и домена {1} на стороне метрики и ожидать ошибку {2}")
    public WebmasterLink confirmLinkAndExpectError(Long counterId, String domain, IExpectedError error, IFormParameters... parameters) {
        return confirmLink(counterId, domain, ERROR_MESSAGE, expectError(error), parameters).getWebmasterLink();
    }

    private ManagementV1CounterCounterIdWebmasterLinkConfirmPOSTSchema confirmLink(Long counterId, String domain, String message, Matcher matcher, IFormParameters... parameters) {
        ManagementV1CounterCounterIdWebmasterLinkConfirmPOSTSchema result =
                executeAsJson(getRequestBuilder(String.format("/management/v1/counter/%s/webmaster_link/confirm", counterId))
                        .post(new EmptyHttpEntity(), makeParameters("domain", domain).append(parameters))).readResponse(ManagementV1CounterCounterIdWebmasterLinkConfirmPOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }
}
