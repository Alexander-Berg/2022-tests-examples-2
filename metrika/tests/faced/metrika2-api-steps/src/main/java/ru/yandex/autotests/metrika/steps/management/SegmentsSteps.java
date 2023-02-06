package ru.yandex.autotests.metrika.steps.management;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.irt.testutils.json.JsonUtils;
import ru.yandex.autotests.metrika.beans.schemes.*;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.handles.SegmentsPathFragment;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.metrika.api.management.client.segments.SegmentsServiceInnerSegmentUsers;
import ru.yandex.qatools.allure.annotations.Step;

import java.util.List;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.httpclient.lite.core.BackEndRequestBuilder.EMPTY_CONTEXT;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addJsonAttachment;

/**
 * Created by konkov on 11.11.2014.
 */
public class SegmentsSteps extends MetrikaBaseSteps {

    private SegmentsPathFragment fragment = SegmentsPathFragment.INTERFACE;

    public SegmentsPathFragment getFragment() {
        return fragment;
    }

    public void setFragment(SegmentsPathFragment fragment) {
        this.fragment = fragment;
    }

    public SegmentsSteps withPathFragment(final SegmentsPathFragment fragment) {
        this.fragment = fragment;
        return this;
    }

    private String getPathFragment() {
        return fragment.getFragment();
    }

    @Step("Получить список сегментов для счетчика {0}")
    public List<Segment> getSegmentsAndExpectSuccess(Long counterId) {
        return getSegments(SUCCESS_MESSAGE, expectSuccess(), counterId).getSegments();
    }

    @Step("Получить список сегментов для счетчика {1} и ожидать ошибку {0}")
    public List<Segment> getSegmentsAndExpectError(IExpectedError error, Long counterId) {
        return getSegments(ERROR_MESSAGE, expectError(error), counterId).getSegments();
    }

    private ManagementV1CounterCounterIdSegmentsGETSchema getSegments(String message, Matcher matcher, Long counterId) {
        ManagementV1CounterCounterIdSegmentsGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/%ssegments",
                        counterId, getPathFragment())).get())
                .readResponse(ManagementV1CounterCounterIdSegmentsGETSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Получить информацию о сегменте {1} для счетчика {0}")
    public Segment getSegmentAndExpectSuccess(
            Long counterId, Long segmentId) {
        return getSegment(SUCCESS_MESSAGE, expectSuccess(), counterId, segmentId).getSegment();
    }

    @Step("Получить информацию о сегменте {2} для счетчика {1} и ожидать ошибку {0}")
    public Segment getSegmentAndExpectError(
            IExpectedError error, Long counterId, Long segmentId) {
        return getSegment(ERROR_MESSAGE, expectError(error), counterId, segmentId).getSegment();
    }

    private ManagementV1CounterCounterIdSegmentSegmentIdGETSchema getSegment(String message, Matcher matcher,
                                                                             Long counterId, Long segmentId) {
        ManagementV1CounterCounterIdSegmentSegmentIdGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/management/v1/counter/%s/%ssegment/%s", counterId,
                        getPathFragment(), segmentId)).get())
                .readResponse(ManagementV1CounterCounterIdSegmentSegmentIdGETSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Создать сегмент для счетчика {0}")
    public Segment createSegmentAndExpectSuccess(Long counterId, Segment segment) {
        return createSegment(SUCCESS_MESSAGE, expectSuccess(), counterId, segment).getSegment();
    }

    @Step("Создать сегмент для счетчика {1} и ожидать ошибку {0}")
    public Segment createSegmentAndExpectError(IExpectedError error, Long counterId, Segment segment) {
        return createSegment(ERROR_MESSAGE, expectError(error), counterId, segment).getSegment();
    }

    @Step("Создать сегменты для счетчика {0}")
    public List<Segment> createSegments(Long counterId, List<Segment> segments) {
        addJsonAttachment(String.format("Всего сегментов %s", segments.size()), JsonUtils.toString(segments));

        return segments.stream()
                .map(operation -> createSegmentAndExpectSuccess(counterId, operation))
                .collect(toList());
    }

    private ManagementV1CounterCounterIdSegmentsPOSTSchema createSegment(
            String message, Matcher matcher, Long counterId, Segment segment) {
        ManagementV1CounterCounterIdSegmentsPOSTSchema result = executeAsJson(
                getRequestBuilder(
                        String.format("/management/v1/counter/%s/%ssegments", counterId, getPathFragment()))
                        .post(new ManagementV1CounterCounterIdSegmentsPOSTRequestSchema().withSegment(segment)))
                .readResponse(ManagementV1CounterCounterIdSegmentsPOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Изменить сегмент {1} для счетчика {0}")
    public Segment editSegmentAndExpectSuccess(Long counterId, Long segmentId, Segment segment) {
        return editSegment(SUCCESS_MESSAGE, expectSuccess(), counterId, segmentId, segment).getSegment();
    }

    @Step("Изменить сегмент {2} для счетчика {1} и ожидать ошибку {0}")
    public Segment editSegmentAndExpectError(IExpectedError error, Long counterId, Long segmentId, Segment segment) {
        return editSegment(ERROR_MESSAGE, expectError(error), counterId, segmentId, segment).getSegment();
    }

    private ManagementV1CounterCounterIdSegmentSegmentIdPUTSchema editSegment(String message, Matcher matcher,
                                                                              Long counterId, Long segmentId,
                                                                              Segment segment) {
        ManagementV1CounterCounterIdSegmentSegmentIdPUTSchema result = executeAsJson(
                getRequestBuilder(
                        String.format("/management/v1/counter/%s/%ssegment/%s",
                                counterId, getPathFragment(), segmentId))
                        .put(new ManagementV1CounterCounterIdSegmentSegmentIdPUTRequestSchema().withSegment(segment)))
                .readResponse(ManagementV1CounterCounterIdSegmentSegmentIdPUTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Удалить сегмент {1} для счетчика {0}")
    public Boolean deleteSegmentAndExpectSuccess(
            Long counterId, Long segmentId) {
        return deleteSegment(SUCCESS_MESSAGE, expectSuccess(), counterId, segmentId).getSuccess();
    }

    @Step("Удалить сегмент {2} для счетчика {1} и ожидать ошибку {0}")
    public Boolean deleteSegmentAndExpectError(
            IExpectedError error, Long counterId, Long segmentId) {
        return deleteSegment(ERROR_MESSAGE, expectError(error), counterId, segmentId).getSuccess();
    }

    private ManagementV1CounterCounterIdSegmentSegmentIdDELETESchema deleteSegment(
            String message, Matcher matcher, Long counterId, Long segmentId) {
        ManagementV1CounterCounterIdSegmentSegmentIdDELETESchema result = executeAsJson(
                getRequestBuilder(
                        String.format("/management/v1/counter/%s/%ssegment/%s", counterId,
                                getPathFragment(), segmentId))
                        .delete(EMPTY_CONTEXT))
                .readResponse(ManagementV1CounterCounterIdSegmentSegmentIdDELETESchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Получение списка сегментов по списку id")
    public List<Segment> getSegmentsAndExpectSuccess(Long counterId, List<Long> segmentIds) {
        return getSegments(SUCCESS_MESSAGE, expectSuccess(), counterId, segmentIds).getSegments();
    }

    @Step("Получение списка сегментов счетчика {1} по списку id и ожидать ошибки {0}")
    public List<Segment> getSegmentsAndExpectError(IExpectedError error, Long counterId, List<Long> segmentIds) {
        return getSegments(ERROR_MESSAGE, expectError(error), counterId, segmentIds).getSegments();
    }

    private ManagementV1CounterCounterIdSegmentsByIdsPOSTSchema getSegments(String message, Matcher matcher,
                                                                            Long counterId, List<Long> segmentIds) {
        ManagementV1CounterCounterIdSegmentsByIdsPOSTSchema result = executeAsJson(
                getRequestBuilder(
                        String.format("/management/v1/counter/%s/%ssegments_by_ids",
                                counterId, getPathFragment()))
                        .post(new ManagementV1CounterCounterIdSegmentsByIdsPOSTRequestSchema()
                                .withSegments(segmentIds)))
                .readResponse(ManagementV1CounterCounterIdSegmentsByIdsPOSTSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

    @Step("Получить список сегментов и статистику для счетчика {0}")
    public List<SegmentsServiceInnerSegmentUsers> getSegmentsStatAndExpectSuccess(Long counterId,
                                                                                  IFormParameters... parameters) {
        return getSegmentsStat(SUCCESS_MESSAGE, expectSuccess(), counterId, parameters).getSegments();
    }

    @Step("Получить список сегментов и статистику для счетчика {1} и ожидать ошибку {0}")
    public List<SegmentsServiceInnerSegmentUsers> getSegmentsStatAndExpectError(IExpectedError error, Long counterId,
                                                                                IFormParameters... parameters) {
        return getSegmentsStat(ERROR_MESSAGE, expectError(error), counterId, parameters).getSegments();
    }

    private InternalManagementV1CounterCounterIdSegmentsUsersGETSchema getSegmentsStat(
            String message, Matcher matcher,
            Long counterId, IFormParameters... parameters) {
        InternalManagementV1CounterCounterIdSegmentsUsersGETSchema result = executeAsJson(
                getRequestBuilder(String.format("/internal/management/v1/counter/%s/segments/users", counterId))
                        .get(parameters))
                .readResponse(InternalManagementV1CounterCounterIdSegmentsUsersGETSchema.class);

        TestSteps.assertThat(message, result, matcher);

        return result;
    }

}
