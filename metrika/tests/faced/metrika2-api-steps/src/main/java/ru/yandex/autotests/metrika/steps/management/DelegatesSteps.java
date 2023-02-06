package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.AddGrantRequest;
import ru.yandex.metrika.api.management.client.AddGrantRequestInnerAddRequestType;
import ru.yandex.metrika.api.management.client.external.DelegateE;
import ru.yandex.metrika.api.management.client.external.DelegateRequestE;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.ArrayList;
import java.util.List;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

/**
 * Created by konkov on 29.12.2014.
 */
public class DelegatesSteps extends MetrikaBaseSteps {

    @Step("Получить список представителей")
    public List<DelegateE> getDelegatesAndExpectSuccess() {
        return getDelegates(SUCCESS_MESSAGE, expectSuccess()).getDelegates();
    }

    @Step("Получить список представителей и ожидать ошибку {0}")
    public List<DelegateE> getDelegatesAndExpectError(IExpectedError error) {
        return getDelegates(ERROR_MESSAGE, expectError(error)).getDelegates();
    }

    private ManagementV1DelegatesGETSchema getDelegates(String message, Matcher matcher) {
        ManagementV1DelegatesGETSchema result = executeAsJson(
                getRequestBuilder("/management/v1/delegates").get())
                .readResponse(ManagementV1DelegatesGETSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить представителя {0}")
    public Boolean deleteDelegateAndExpectSuccess(String login) {
        return deleteDelegate(SUCCESS_MESSAGE, expectSuccess(), login).getSuccess();
    }

    @Step("Удалить представителя {1} и ожидать ошибку {0}")
    public Boolean deleteDelegateAndExpectError(IExpectedError error, String login) {
        return deleteDelegate(ERROR_MESSAGE, expectError(error), login).getSuccess();
    }

    @Step("Удалить представителя {0} и игнорировать результат")
    public Boolean deleteDelegateAndIgnoreStatus(String login) {
        return deleteDelegate(ANYTHING_MESSAGE, expectAnything(), login).getSuccess();
    }

    private ManagementV1DelegateDELETESchema deleteDelegate(String message, Matcher matcher, String login) {
        ManagementV1DelegateDELETESchema result = executeAsJson(
                getRequestBuilder("/management/v1/delegate")
                        .delete(makeParameters("user_login", login)))
                .readResponse(ManagementV1DelegateDELETESchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Добавить представителя")
    public List<DelegateE> addDelegateAndExpectSuccess(
            DelegateE delegate, IFormParameters... parameters) {
        return addDelegate(SUCCESS_MESSAGE, expectSuccess(), delegate, parameters).getDelegates();
    }

    @Step("Добавить представителя и ожидать ошибку {0}")
    public List<DelegateE> addDelegateAndExpectError(
            IExpectedError error, DelegateE delegate, IFormParameters... parameters) {
        return addDelegate(ERROR_MESSAGE, expectError(error), delegate, parameters).getDelegates();
    }

    private ManagementV1DelegatesPOSTSchema addDelegate(String message, Matcher matcher,
                                                        DelegateE delegate, IFormParameters... parameters) {
        ManagementV1DelegatesPOSTSchema result = executeAsJson(
                getRequestBuilder("/management/v1/delegates")
                        .post(new ManagementV1DelegatesPOSTRequestSchema().withDelegate(delegate),
                                parameters))
                .readResponse(ManagementV1DelegatesPOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Запросить представительство у {0} для {1}")
    public void requestDelegateAndExpectSuccess(String delegatorLogin, String delegateLogin) {
        InternalGrantRequestsPOSTSchema result = executeAsJson(
                getRequestBuilder("/internal/grant_requests")
                        .post(new InternalGrantRequestsPOSTRequestSchema()
                                .withRequests(requestDelegate(delegatorLogin, delegateLogin))))
                .readResponse(InternalGrantRequestsPOSTSchema.class);

        TestSteps.assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

    private List<AddGrantRequest> requestDelegate(String delegatorLogin, String delegateLogin) {
        List<AddGrantRequest> result = new ArrayList<>();
        result.add(new AddGrantRequest().withLang("ru")
                .withPermission("RO")
                .withObjectType(AddGrantRequestInnerAddRequestType.DELEGATE)
                .withServiceName("direct")
                .withObjectId(delegatorLogin)
                .withOwnerLogin(delegatorLogin)
                .withRequestorLogin(delegateLogin));

        return result;
    }

    @Step("Получить список запросов на представительство")
    public List<DelegateRequestE> getDelegateRequests() {
        return executeAsJson(getRequestBuilder("/management/v1/delegates_requests").get())
                .readResponse(ManagementV1DelegatesRequestsGETSchema.class).getDelegatesRequests();
    }

    @Step("Подтвердить представителя {0}")
    public void acceptDelegateRequestAndExpectSuccess(String login) {
        DelegateRequestE delegateRequest = new DelegateRequestE().withUserLogin(login).withVote(true);
        ManagementV1VoteDelegateRequestPOSTSchema result = voteDelegateRequest(delegateRequest);

        TestSteps.assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

    @Step("Отклонить представителя {0}")
    public void rejectDelegateRequestAndExpectSuccess(String login) {
        DelegateRequestE delegateRequest = new DelegateRequestE().withUserLogin(login).withVote(false);
        ManagementV1VoteDelegateRequestPOSTSchema result = voteDelegateRequest(delegateRequest);

        TestSteps.assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

    private ManagementV1VoteDelegateRequestPOSTSchema voteDelegateRequest(DelegateRequestE delegateRequest) {
        return executeAsJson(
                getRequestBuilder("/management/v1/vote_delegate_request")
                        .post(new ManagementV1VoteDelegateRequestPOSTRequestSchema()
                                .withDelegateRequest(delegateRequest)))
                .readResponse(ManagementV1VoteDelegateRequestPOSTSchema.class);
    }
}
