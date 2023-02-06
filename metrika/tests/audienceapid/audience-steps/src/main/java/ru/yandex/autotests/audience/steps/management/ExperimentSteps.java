package ru.yandex.autotests.audience.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.audience.segmentab.ExperimentAB;
import ru.yandex.autotests.audience.beans.schemes.*;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

public class ExperimentSteps extends HttpClientLiteFacade {

    public ExperimentSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список экспериментов")
    public List<ExperimentAB> getExperiments(IFormParameters... parameters) {
        return getExperiments(SUCCESS_MESSAGE, expectSuccess(), parameters).getExperiments();
    }

    @Step("Получить список экспериментов и ожидать ошибку {0}")
    public List<ExperimentAB> getExperimentsAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getExperiments(ERROR_MESSAGE, expectError(error), parameters).getExperiments();
    }

    private V1ManagementExperimentsGETSchema getExperiments(String message, Matcher matcher, IFormParameters... parameters) {
        V1ManagementExperimentsGETSchema result = get(V1ManagementExperimentsGETSchema.class,
                "/v1/management/experiments", parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Добавить эксперимент {0}")
    public ExperimentAB createExperiment(ExperimentAB experiment, IFormParameters... parameters) {
        return createExperiment(SUCCESS_MESSAGE, expectSuccess(), experiment, parameters).getExperiment();
    }

    @Step("Добавить эксперимент {1} - и ожидать ошибку {0}")
    public ExperimentAB createExperimentAndExpectError(IExpectedError error, ExperimentAB experiment,
                                                       IFormParameters... parameters) {
        return createExperiment(ERROR_MESSAGE, expectError(error), experiment, parameters).getExperiment();
    }

    private V1ManagementExperimentsPOSTSchema createExperiment(String message, Matcher matcher,
                                                               ExperimentAB experiment, IFormParameters... parameters) {
        V1ManagementExperimentsPOSTSchema result = post(V1ManagementExperimentsPOSTSchema.class,
                "/v1/management/experiments",
                new V1ManagementExperimentsPOSTRequestSchema().withExperiment(experiment),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Добавить эксперимент монетизации {0}")
    public ExperimentAB createBkExperiment(ExperimentAB experiment, IFormParameters... parameters) {
        return createBkExperiment(SUCCESS_MESSAGE, expectSuccess(), experiment, parameters).getExperiment();
    }

    private V1ManagementExperimentsPOSTSchema createBkExperiment(String message, Matcher matcher,
                                                               ExperimentAB experiment, IFormParameters... parameters) {
        V1ManagementExperimentsPOSTSchema result = post(V1ManagementExperimentsPOSTSchema.class,
                "/v1/management/experiments_monetize",
                new V1ManagementExperimentsPOSTRequestSchema().withExperiment(experiment),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Редактировать эксперимент {0}")
    public ExperimentAB editExperiment(Long id, ExperimentAB experiment, IFormParameters... parameters) {
        return editExperiment(id, SUCCESS_MESSAGE, expectSuccess(), experiment, parameters).getExperiment();
    }

    @Step("Редактировать эксперимент {1} - и ожидать ошибку {0}")
    public ExperimentAB editExperimentAndExpectError(Long id, IExpectedError error, ExperimentAB experiment,
                                                     IFormParameters... parameters) {
        return editExperiment(id, ERROR_MESSAGE, expectError(error), experiment, parameters).getExperiment();
    }

    private V1ManagementExperimentExperimentIdPUTSchema editExperiment(Long id, String message, Matcher matcher,
                                                               ExperimentAB experiment, IFormParameters... parameters) {
        V1ManagementExperimentExperimentIdPUTSchema result = put(V1ManagementExperimentExperimentIdPUTSchema.class,
                format("/v1/management/experiment/%s", id),
                new V1ManagementExperimentExperimentIdPUTRequestSchema().withExperiment(experiment),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить эксперимент {0}")
    public Boolean deleteExperiment(Long id, IFormParameters... parameters) {
        return deleteExperiment(SUCCESS_MESSAGE, expectSuccess(), id, parameters).getSuccess();
    }

    @Step("Удалить эксперимент {1} и ожидать ошибку {0}")
    public Boolean deleteExperimentAndExpectError(IExpectedError error, Long id, IFormParameters... parameters) {
        return deleteExperiment(ERROR_MESSAGE, expectError(error), id, parameters).getSuccess();
    }

    @Step("Удалить эксперимент {0} и игнорировать статус")
    public Boolean deleteExperimentAndIgnoreStatus(Long id, IFormParameters... parameters) {
        if (id != null) {
            return deleteExperiment(ANYTHING_MESSAGE, expectAnything(), id, parameters).getSuccess();
        } else {
            return true;
        }
    }

    private V1ManagementExperimentExperimentIdDELETESchema deleteExperiment(String message, Matcher matcher, Long id,
                                                                                               IFormParameters... parameters) {
        V1ManagementExperimentExperimentIdDELETESchema result = delete(V1ManagementExperimentExperimentIdDELETESchema.class,
                format("/v1/management/experiment/%s", id),
                makeParameters().append(parameters));

        assertThat(message, result, matcher);

        return result;
    }

    @Step("Восстановить эксперимент {0}")
    public Boolean restoreExperiment(Long experimentId, IFormParameters... parameters) {
        return restoreExperiment(SUCCESS_MESSAGE, expectSuccess(), experimentId, parameters).getSuccess();
    }

    @Step("Восстановить эксперимент {1} и ожидать ошибку {0}")
    public Boolean restoreExperimentAndExpectError(IExpectedError error, Long experimentId, IFormParameters... parameters) {
        return restoreExperiment(ERROR_MESSAGE, expectError(error), experimentId, parameters).getSuccess();
    }

    private V1ManagementExperimentRestoreExperimentIdPOSTSchema restoreExperiment(String message, Matcher matcher,
                                                                        Long experimentId, IFormParameters... parameters) {
        V1ManagementExperimentRestoreExperimentIdPOSTSchema result = post(V1ManagementExperimentRestoreExperimentIdPOSTSchema.class,
                format("/v1/management/experiment/restore/%s", experimentId), null, parameters);

        assertThat(message, result, matcher);

        return result;
    }

}
