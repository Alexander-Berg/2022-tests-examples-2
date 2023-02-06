package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.dao.MobSegment;
import ru.yandex.metrika.mobmet.model.request.SegmentConversionForFilterByNsRequest;
import ru.yandex.metrika.mobmet.model.request.SegmentConversionForReportByNsRequest;
import ru.yandex.metrika.mobmet.model.request.SegmentConversionForReportByTableRequest;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;


public class SegmentsSteps extends AppMetricaBaseSteps {

    public SegmentsSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить сегмент {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public MobSegment getSegment(Long appId, Long segmentId) {
        return getSegment(SUCCESS_MESSAGE, expectSuccess(), appId, segmentId).getSegment();
    }

    @Step("Получить сегмент {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public MobSegment getSegmentAndExpectError(Long appId, Long segmentId, IExpectedError error) {
        return getSegment(ERROR_MESSAGE, expectError(error), appId, segmentId).getSegment();
    }

    @Step("Получить список сегментов для приложения {0}")
    @ParallelExecution(ALLOW)
    public List<MobSegment> getSegmentsList(Long appId) {
        return getSegmentsList(SUCCESS_MESSAGE, expectSuccess(), appId).getSegments();
    }

    @Step("Добавить сегмент для приложения {0}")
    @ParallelExecution(ALLOW)
    public MobSegment addSegment(Long appId, MobSegment segment) {
        return addSegment(SUCCESS_MESSAGE, expectSuccess(), appId, segment).getSegment();
    }

    @Step("Обновить сегмент {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public MobSegment updateSegment(Long appId, Long segmentId, MobSegment segment) {
        return updateSegment(SUCCESS_MESSAGE, expectSuccess(), appId, segmentId, segment).getSegment();
    }

    @Step("Удалить сегмент {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void deleteSegment(Long appId, Long segmentId) {
        deleteSegment(SUCCESS_MESSAGE, expectSuccess(), appId, segmentId);
    }

    @Step("Удалить сегмент {1} для приложения {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteSegmentAndIgnoreResult(Long appId, Long segmentId) {
        deleteSegment(ANYTHING_MESSAGE, expectSuccess(), appId, segmentId);
    }

    @Step("Преобразовать сегмент для namespace {0}")
    @ParallelExecution(ALLOW)
    public String convertFrontendSegmentByNsForReport(String ns, String segment) {
        return convertFrontendSegmentByNsForReport(SUCCESS_MESSAGE, expectSuccess(), ns, segment).getResponse();
    }

    @Step("Преобразовать сегмент для фильтра с namespace {1} и отчёта с namespace {0}")
    @ParallelExecution(ALLOW)
    public String convertFrontendSegmentByNsForFilterValues(String reportNs, String filterNs, String segment) {
        return convertFrontendSegmentByNsForFilterValues(SUCCESS_MESSAGE, expectSuccess(), reportNs, filterNs, segment)
                .getResponse();
    }

    @Step("Преобразовать сегмент для таблицы {0}")
    @ParallelExecution(ALLOW)
    public String convertFrontendSegmentByTable(String table, String segment) {
        return convertFrontendSegmentByTable(SUCCESS_MESSAGE, expectSuccess(), table, segment).getResponse();
    }

    private ManagementV2ApplicationApiKeySegmentIdGETSchema getSegment(String message, Matcher matcher,
                                                                       Long appId, Long segmentId) {
        final ManagementV2ApplicationApiKeySegmentIdGETSchema result = get(
                ManagementV2ApplicationApiKeySegmentIdGETSchema.class,
                String.format("/management/v2/application/%s/segment/%s", appId, segmentId));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV2ApplicationApiKeySegmentsGETSchema getSegmentsList(String message, Matcher matcher, Long appId) {
        final ManagementV2ApplicationApiKeySegmentsGETSchema result = get(
                ManagementV2ApplicationApiKeySegmentsGETSchema.class,
                String.format("/management/v2/application/%s/segments", appId));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV2ApplicationApiKeySegmentsPOSTSchema addSegment(String message, Matcher matcher,
                                                                       Long appId, MobSegment segment) {
        final ManagementV2ApplicationApiKeySegmentsPOSTSchema result = post(
                ManagementV2ApplicationApiKeySegmentsPOSTSchema.class,
                String.format("/management/v2/application/%s/segments", appId),
                new ManagementV2ApplicationApiKeySegmentsPOSTRequestSchema().withSegment(segment));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV2ApplicationApiKeySegmentIdPUTSchema updateSegment(String message, Matcher matcher,
                                                                          Long appId, Long segmentId, MobSegment segment) {
        final ManagementV2ApplicationApiKeySegmentIdPUTSchema result = put(
                ManagementV2ApplicationApiKeySegmentIdPUTSchema.class,
                String.format("/management/v2/application/%s/segment/%s", appId, segmentId),
                new ManagementV2ApplicationApiKeySegmentIdPUTRequestSchema().withSegment(segment));

        assertThat(message, result, matcher);

        return result;
    }

    private void deleteSegment(String message, Matcher matcher, Long appId, Long segmentId) {
        final ManagementV2ApplicationApiKeySegmentIdDELETESchema result = delete(
                ManagementV2ApplicationApiKeySegmentIdDELETESchema.class,
                String.format("/management/v2/application/%s/segment/%s", appId, segmentId));

        assertThat(message, result, matcher);
    }

    private InternalV1SegmentConvertByNsPOSTSchema convertFrontendSegmentByNsForFilterValues(
            String message, Matcher matcher, String reportNs, String filterNs, String segment) {
        final InternalV1SegmentConvertByNsPOSTSchema result = post(
                InternalV1SegmentConvertByNsPOSTSchema.class,
                "/internal/v1/segment/filter_values/convert_by_ns",
                new SegmentConversionForFilterByNsRequest()
                        .withReportNamespace(reportNs)
                        .withFilterNamespace(filterNs)
                        .withParams(segment));

        assertThat(message, result, matcher);

        return result;
    }

    private InternalV1SegmentFilterValuesConvertByNsPOSTSchema convertFrontendSegmentByNsForReport(String message, Matcher matcher,
                                                                                                   String ns, String segment) {
        final InternalV1SegmentFilterValuesConvertByNsPOSTSchema result = post(
                InternalV1SegmentFilterValuesConvertByNsPOSTSchema.class,
                "/internal/v1/segment/report/convert_by_ns",
                new SegmentConversionForReportByNsRequest().withNamespace(ns).withParams(segment));

        assertThat(message, result, matcher);

        return result;
    }

    private InternalV1SegmentReportConvertByTablePOSTSchema convertFrontendSegmentByTable(String message, Matcher matcher,
                                                                                          String table, String segment) {
        final InternalV1SegmentReportConvertByTablePOSTSchema result = post(
                InternalV1SegmentReportConvertByTablePOSTSchema.class,
                "/internal/v1/segment/report/convert_by_table",
                new SegmentConversionForReportByTableRequest().withTable(table).withParams(segment));

        assertThat(message, result, matcher);

        return result;
    }
}
