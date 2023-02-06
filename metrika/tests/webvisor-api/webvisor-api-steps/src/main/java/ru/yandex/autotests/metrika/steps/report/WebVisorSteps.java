package ru.yandex.autotests.metrika.steps.report;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.Collections;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.errors.CustomError.expect;

/**
 * Created by konkov on 09.12.2014.
 */
public class WebVisorSteps extends BaseReportSteps {

    @Step("Построить отчет вебвизора по визитам")
    public WebvisorV2DataVisitsGETSchema getVisitsGridAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.WEBVISOR_VISITS_GRID, parameters);
    }

    @Step("Построить отчет вебвизора по визитам и ожидать ошибки {0} {1}")
    public WebvisorV2DataVisitsGETSchema getVisitsGridAndExpectError(Long code, String message,
                                                                     IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.WEBVISOR_VISITS_GRID, expect(code, message), parameters);
    }

    @Step("Построить отчет вебвизора по просмотрам для визита")
    public WebvisorV2DataHitsGETSchema getHitsGridAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.WEBVISOR_HITS_GRID, parameters);
    }

    @Step("Построить отчет вебвизора по просмотрам и ожидать ошибки {0} {1}")
    public WebvisorV2DataHitsGETSchema getHitsGridAndExpectError(IExpectedError error,
                                                                 IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.WEBVISOR_HITS_GRID, error, parameters);
    }

    @Step("Добавить визит в избранное")
    public void addSelectedVisitsAndExpectSuccess(IFormParameters... parameters) {
        addSelectedVisits(SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    private void addSelectedVisits(String message, Matcher matcher, IFormParameters... parameters) {
        WebvisorV2DataFavoritesAddPOSTSchema result = executeAsJson(
                getRequestBuilder("/webvisor/v2/data/favorites_add").post(Collections.emptyList(), parameters))
                .readResponse(WebvisorV2DataFavoritesAddPOSTSchema.class);

        assertThat(message, result, matcher);
    }

    @Step("Удалить визит из избранного")
    public void deleteSelectedVisitAndExpectSuccess(IFormParameters... parameters) {
        deleteSelectedVisit(SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    private void deleteSelectedVisit(String message, Matcher matcher, IFormParameters... parameters) {
        WebvisorV2DataFavoritesRemovePOSTSchema result = executeAsJson(
                getRequestBuilder("/webvisor/v2/data/favorites_remove").post(Collections.emptyList(), parameters))
                .readResponse(WebvisorV2DataFavoritesRemovePOSTSchema.class);

        assertThat(message, result, matcher);
    }

    @Step("Пометить визит просмотренным")
    public void markedVisitViewedAndExpectSuccess(IFormParameters... parameters) {
        markedVisitViewed(SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    private void markedVisitViewed(String message, Matcher matcher, IFormParameters... parameters) {
        WebvisorV2DataViewedAddPOSTSchema result = executeAsJson(
                getRequestBuilder("/webvisor/v2/data/viewed_add").post(Collections.emptyList(), parameters))
                .readResponse(WebvisorV2DataViewedAddPOSTSchema.class);

        assertThat(message, result, matcher);
    }

    @Step("Пометить визит не просмотренным")
    public void markedVisitUnviewedAndExpectSuccedd(IFormParameters... parameters) {
        markedVisitUnviewed(SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    private void markedVisitUnviewed(String message, Matcher matcher, IFormParameters... parameters) {
        WebvisorV2DataViewedRemovePOSTSchema result = executeAsJson(
                getRequestBuilder("/webvisor/v2/data/viewed_remove").post(Collections.emptyList(), parameters))
                .readResponse(WebvisorV2DataViewedRemovePOSTSchema.class);

        assertThat(message, result, matcher);
    }


}
