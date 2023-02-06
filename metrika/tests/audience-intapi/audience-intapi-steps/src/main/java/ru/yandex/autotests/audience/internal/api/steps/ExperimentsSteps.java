package ru.yandex.autotests.audience.internal.api.steps;

import ru.yandex.audience.internal.InternalV1ExperimentGETSchema;
import ru.yandex.audience.internal.InternalV1ExperimentSegmentGETSchema;
import ru.yandex.audience.internal.InternalV1ExperimentSegmentsGETSchema;
import ru.yandex.audience.internal.InternalV1ExperimentsGETSchema;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;

public class ExperimentsSteps extends HttpClientLiteFacade {

    public ExperimentsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Успешно получить эксперимент")
    public InternalV1ExperimentGETSchema getExperiment(IFormParameters... parameters) {
        return get(InternalV1ExperimentGETSchema.class, "/internal/v1/experiment", parameters);
    }

    @Step("Пытаться получить эксперимент и ожидать ошибку {0}")
    public InternalV1ExperimentGETSchema getExperimentAndExpectError(IExpectedError error, IFormParameters... parameters) {
        InternalV1ExperimentGETSchema result = get(InternalV1ExperimentGETSchema.class, "/internal/v1/experiment", parameters);

        assertThat(ERROR_MESSAGE, result, expectError(error));

        return result;
    }

    @Step("Получить сегмент эксперимента")
    public InternalV1ExperimentSegmentGETSchema getExperimentSegment(IFormParameters... parameters) {
        return get(InternalV1ExperimentSegmentGETSchema.class, "/internal/v1/experiment_segment", parameters);
    }

    @Step("Получить сегменты эксперимента")
    public InternalV1ExperimentSegmentsGETSchema getExperimentSegments(IFormParameters... parameters) {
        return get(InternalV1ExperimentSegmentsGETSchema.class, "/internal/v1/experiment_segments", parameters);
    }

    @Step("Получить эксперименты cчетчика")
    public InternalV1ExperimentsGETSchema getExperiments(IFormParameters... parameters) {
        return get(InternalV1ExperimentsGETSchema.class, "/internal/v1/experiments", parameters);
    }
}
