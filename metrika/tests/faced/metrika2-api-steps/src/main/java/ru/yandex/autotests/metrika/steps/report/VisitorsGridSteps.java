package ru.yandex.autotests.metrika.steps.report;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.utils.EmptyHttpEntity;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

public class VisitorsGridSteps extends BaseReportSteps {

    @Step("Построить отчет по посетителям")
    public StatV1UserListGETSchema getVisitorsGridAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.VISITORS_GRID, parameters);
    }

    @Step("Построить отчет по посетителям и ожидать ошибку {0}")
    public StatV1UserListGETSchema getVisitorsGridAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.VISITORS_GRID, error, parameters);
    }

    @Step("Получить информацию по посетителю")
    public StatV1UserInfoGETSchema getVisitorInfoAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.VISITOR_INFO, parameters);
    }

    @Step("Получить информацию по посетителю и ожидать ошибку {0}")
    public StatV1UserInfoGETSchema getVisitorInfoAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.VISITOR_INFO, error, parameters);
    }

    @Step("Получить список визитов посетителя")
    public StatV1UserVisitsGETSchema getVisitorVisitsAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.VISITOR_VISITS, parameters);
    }

    @Step("Получить список визитов посетителя и ожидать ошибку {0}")
    public StatV1UserVisitsGETSchema getVisitorVisitsAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.VISITOR_VISITS, error, parameters);
    }

    @Step("Добавить постетителю комментарий")
    public void addCommentAndExpectSuccess(IFormParameters... parameters) {
        addComment(SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    @Step("Добавить посетителю комментарий и ожидать ошибку {0}")
    public void addCommentAndExpectError(IExpectedError error, IFormParameters... parameters) {
        addComment(ERROR_MESSAGE, expectErrorCode(error.getCode()), parameters);
    }


    private void addComment(String message, Matcher matcher, IFormParameters... parameters) {
        ManagementV1UserCommentsPOSTSchema response =
                executeAsJson(getRequestBuilder("/management/v1/user/comments").post(new EmptyHttpEntity(), parameters))
                .readResponse(ManagementV1UserCommentsPOSTSchema.class);

        assertThat(message, response, matcher);
    }

    @Step("Удалить комментарий к посетителю")
    public void deleteCommentAndExpectSuccess(IFormParameters... parameters) {
        deleteComment(SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    @Step("Удалить комментарий к посетителю и ожидать ошибку {0}")
    public void deleteCommentAndExpectError(IExpectedError error, IFormParameters... parameters) {
        deleteComment(ERROR_MESSAGE, expectErrorCode(error.getCode()), parameters);
    }


    private void deleteComment(String message, Matcher matcher, IFormParameters... parameters) {
        ManagementV1UserCommentsDELETESchema response =
                executeAsJson(getRequestBuilder("/management/v1/user/comments").delete(null, parameters))
                        .readResponse(ManagementV1UserCommentsDELETESchema.class);

        assertThat(message, response, matcher);
    }

}
