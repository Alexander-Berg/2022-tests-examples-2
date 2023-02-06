package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.beans.schemes.InternalWebmasterLinkConfirmPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalWebmasterLinkCreatePOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalWebmasterLinkDeletePOSTSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.webmaster.WebmasterLink;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

public class WebmasterLinkInternalSteps extends MetrikaBaseSteps {

    @Step("Создать привязку для счетчика {0} и домена {1} на стороне вебмастера")
    public WebmasterLink createLinkAndExpectSuccess(Long counterId, String domain, Long uid, IFormParameters... parameters) {
        return createLink(counterId, domain, uid, SUCCESS_MESSAGE, expectSuccess(), parameters).getWebmasterLink();
    }

    @Step("Создать привязку для счетчика {0} и домена {1} на стороне вебмастера и ожидать ошибку {2}")
    public WebmasterLink createLinkAndExpectError(Long counterId, String domain, Long uid, IExpectedError error, IFormParameters... parameters) {
        return createLink(counterId, domain, uid, ERROR_MESSAGE, expectError(error), parameters).getWebmasterLink();
    }

    private InternalWebmasterLinkCreatePOSTSchema createLink(Long counterId, String domain, Long uid, String message, Matcher matcher, IFormParameters... parameters) {
        InternalWebmasterLinkCreatePOSTSchema result =
                executeAsJson(getRequestBuilder("/internal/webmaster/link/create")
                        .post(makeParameters("domain", domain).append("counter_id", counterId).append("uid", uid).append(parameters)))
                        .readResponse(InternalWebmasterLinkCreatePOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить привязку для счетчика {0} и домена {1} на стороне вебмастера")
    public WebmasterLink deleteLinkAndExpectSuccess(Long counterId, String domain, Long uid, IFormParameters... parameters) {
        return deleteLink(counterId, domain, uid, SUCCESS_MESSAGE, expectSuccess(), parameters).getWebmasterLink();
    }

    @Step("Удалить привязку для счетчика {0} и домена {1} на стороне вебмастера и ожидать ошибку {2}")
    public WebmasterLink deleteLinkAndExpectError(Long counterId, String domain, Long uid, IExpectedError error, IFormParameters... parameters) {
        return deleteLink(counterId, domain, uid, ERROR_MESSAGE, expectError(error), parameters).getWebmasterLink();
    }

    @Step("Удалить привязку для счетчика {0} и домена {1} на стороне вебмастера и игнорировать результат")
    public WebmasterLink deleteLinkAndExpectError(Long counterId, String domain, Long uid, IFormParameters... parameters) {
        return deleteLink(counterId, domain, uid, ANYTHING_MESSAGE, expectAnything(), parameters).getWebmasterLink();
    }

    private InternalWebmasterLinkDeletePOSTSchema deleteLink(Long counterId, String domain, Long uid, String message, Matcher matcher, IFormParameters... parameters) {
        InternalWebmasterLinkDeletePOSTSchema result =
                executeAsJson(getRequestBuilder("/internal/webmaster/link/delete")
                        .post(makeParameters("domain", domain).append("counter_id", counterId).append("uid", uid).append(parameters)))
                        .readResponse(InternalWebmasterLinkDeletePOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Подтвердить привязку для счетчика {0} и домена {1} на стороне вебмастера")
    public WebmasterLink confirmLinkAndExpectSuccess(Long counterId, String domain, Long uid, IFormParameters... parameters) {
        return confirmLink(counterId, domain, uid, SUCCESS_MESSAGE, expectSuccess(), parameters).getWebmasterLink();
    }

    @Step("Подтвердить привязку для счетчика {0} и домена {1} на стороне вебмастера и ожидать ошибку {2}")
    public WebmasterLink confirmLinkAndExpectError(Long counterId, String domain, Long uid, IExpectedError error, IFormParameters... parameters) {
        return confirmLink(counterId, domain, uid, ERROR_MESSAGE, expectError(error), parameters).getWebmasterLink();
    }

    private InternalWebmasterLinkConfirmPOSTSchema confirmLink(Long counterId, String domain, Long uid, String message, Matcher matcher, IFormParameters... parameters) {
        InternalWebmasterLinkConfirmPOSTSchema result =
                executeAsJson(getRequestBuilder("/internal/webmaster/link/confirm")
                        .post(makeParameters("domain", domain).append("counter_id", counterId).append("uid", uid).append(parameters)))
                        .readResponse(InternalWebmasterLinkConfirmPOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }
}
