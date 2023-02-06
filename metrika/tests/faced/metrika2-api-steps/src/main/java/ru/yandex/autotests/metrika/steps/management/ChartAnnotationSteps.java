package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.external.chartannotation.MetrikaChartAnnotation;
import ru.yandex.metrika.util.wrappers.MetrikaChartAnnotationWrapper;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static ru.yandex.autotests.httpclient.lite.core.BackEndRequestBuilder.EMPTY_CONTEXT;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * @author zgmnkv
 */
public class ChartAnnotationSteps extends MetrikaBaseSteps {

    private static final String CHART_ANNOTATIONS_URL = "/management/v1/counter/%d/chart_annotations";
    private static final String CHART_ANNOTATION_URL = "/management/v1/counter/%d/chart_annotation/%d";

    @Step("Создать примечание для счетчика {0}")
    public MetrikaChartAnnotation createAnnotation(Long counterId, MetrikaChartAnnotation annotation) {
        return createAnnotation(SUCCESS_MESSAGE, expectSuccess(), counterId, annotation);
    }

    @Step("Создать примечание для счетчика {1} и ожидать ошибку {0}")
    public MetrikaChartAnnotation createAnnotationAndExpectError(
            IExpectedError error, Long counterId, MetrikaChartAnnotation annotation
    ) {
        return createAnnotation(ERROR_MESSAGE, expectError(error), counterId, annotation);
    }

    @Step("Изменить примечание {1} для счетчика {0}")
    public MetrikaChartAnnotation editAnnotation(Long counterId, Long annotationId, MetrikaChartAnnotation annotation) {
        return editAnnotation(SUCCESS_MESSAGE, expectSuccess(), counterId, annotationId, annotation);
    }

    @Step("Изменить примечание {2} для счетчика {1} и ожидать ошибку {0}")
    public MetrikaChartAnnotation editAnnotationAndExpectError(
            IExpectedError error, Long counterId, Long annotationId, MetrikaChartAnnotation annotation
    ) {
        return editAnnotation(ERROR_MESSAGE, expectError(error), counterId, annotationId, annotation);
    }

    @Step("Удалить примечание {1} для счетчика {0}")
    public void deleteAnnotation(Long counterId, Long annotationId) {
        deleteAnnotation(SUCCESS_MESSAGE, expectSuccess(), counterId, annotationId);
    }

    @Step("Удалить примечание {2} для счетчика {1} и ожидать ошибку {0}")
    public void deleteAnnotationAndExpectError(IExpectedError error, Long counterId, Long annotationId) {
        deleteAnnotation(ERROR_MESSAGE, expectError(error), counterId, annotationId);
    }

    @Step("Получить информацию о примечании {1} для счетчика {0}")
    public MetrikaChartAnnotation getAnnotation(Long counterId, Long annotationId) {
        return getAnnotation(SUCCESS_MESSAGE, expectSuccess(), counterId, annotationId);
    }

    @Step("Получить информацию о примечании {2} для счетчика {1} и ожидать ошибку {0}")
    public MetrikaChartAnnotation getAnnotationAndExpectError(IExpectedError error, Long counterId, Long annotationId) {
        return getAnnotation(ERROR_MESSAGE, expectError(error), counterId, annotationId);
    }

    @Step("Получить список примечаний для счетчика {0}")
    public List<MetrikaChartAnnotation> getAnnotations(Long counterId) {
        return getAnnotations(SUCCESS_MESSAGE, expectSuccess(), counterId);
    }

    @Step("Получить список примечаний для счетчика {1} и ожидать ошибку {0}")
    public List<MetrikaChartAnnotation> getAnnotationsAndExpectError(IExpectedError error, Long counterId) {
        return getAnnotations(ERROR_MESSAGE, expectError(error), counterId);
    }

    private MetrikaChartAnnotation createAnnotation(
            String message, Matcher matcher, Long counterId, MetrikaChartAnnotation annotation
    ) {
        ManagementV1CounterCounterIdChartAnnotationsPOSTSchema result = executeAsJson(
                getRequestBuilder(String.format(CHART_ANNOTATIONS_URL, counterId)).post(
                        new MetrikaChartAnnotationWrapper().withChartAnnotation(annotation)
                )
        ).readResponse(ManagementV1CounterCounterIdChartAnnotationsPOSTSchema.class);

        assertThat(message, result, matcher);

        return result.getChartAnnotation();
    }

    private MetrikaChartAnnotation editAnnotation(
            String message, Matcher matcher, Long counterId, Long annotationId, MetrikaChartAnnotation annotation
    ) {
        ManagementV1CounterCounterIdChartAnnotationIdPUTSchema result = executeAsJson(
                getRequestBuilder(String.format(CHART_ANNOTATION_URL, counterId, annotationId)).put(
                        new MetrikaChartAnnotationWrapper().withChartAnnotation(annotation)
                )
        ).readResponse(ManagementV1CounterCounterIdChartAnnotationIdPUTSchema.class);

        assertThat(message, result, matcher);

        return result.getChartAnnotation();
    }

    private void deleteAnnotation(String message, Matcher matcher, Long counterId, Long annotationId) {
        ManagementV1CounterCounterIdChartAnnotationIdDELETESchema result = executeAsJson(
                getRequestBuilder(String.format(CHART_ANNOTATION_URL, counterId, annotationId)).delete(EMPTY_CONTEXT)
        ).readResponse(ManagementV1CounterCounterIdChartAnnotationIdDELETESchema.class);

        assertThat(message, result, matcher);
    }

    private MetrikaChartAnnotation getAnnotation(String message, Matcher matcher, Long counterId, Long annotationId) {
        ManagementV1CounterCounterIdChartAnnotationIdGETSchema result = executeAsJson(
                getRequestBuilder(String.format(CHART_ANNOTATION_URL, counterId, annotationId)).get()
        ).readResponse(ManagementV1CounterCounterIdChartAnnotationIdGETSchema.class);

        assertThat(message, result, matcher);

        return result.getChartAnnotation();
    }

    private List<MetrikaChartAnnotation> getAnnotations(String message, Matcher matcher, Long counterId) {
        ManagementV1CounterCounterIdChartAnnotationsGETSchema result = executeAsJson(
                getRequestBuilder(String.format(CHART_ANNOTATIONS_URL, counterId)).get()
        ).readResponse(ManagementV1CounterCounterIdChartAnnotationsGETSchema.class);

        assertThat(message, result, matcher);

        return result.getChartAnnotations();
    }
}
