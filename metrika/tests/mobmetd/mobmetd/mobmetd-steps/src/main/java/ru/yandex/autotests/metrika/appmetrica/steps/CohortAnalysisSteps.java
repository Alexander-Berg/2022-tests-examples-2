package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;
import java.util.List;
import java.util.stream.Collectors;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.httpclientlite.core.RequestBuilder;
import ru.yandex.autotests.irt.testutils.allure.AssumptionException;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.V1CohortAnalysisGETSchema;
import ru.yandex.autotests.metrika.appmetrica.parameters.CACohortType;
import ru.yandex.autotests.metrika.appmetrica.parameters.CohortAnalysisParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.cohort.model.CACohortTotals;
import ru.yandex.metrika.mobmet.cohort.model.CAResponse;
import ru.yandex.metrika.mobmet.cohort.model.CARow;
import ru.yandex.metrika.mobmet.cohort.model.cell.CACell;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.aggregate;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Created by graev on 30/01/2017.
 */
public class CohortAnalysisSteps extends AppMetricaBaseSteps {
    public CohortAnalysisSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить отчет по когортному анализу")
    @ParallelExecution(RESTRICT)
    public CAResponse getReportUnwrapped(IFormParameters parameters) {
        return getReport(SUCCESS_MESSAGE, expectSuccess(), parameters).getCohortAnalysisData();
    }

    @Step("Получить отчет по когортному анализу")
    @ParallelExecution(RESTRICT)
    public V1CohortAnalysisGETSchema getReport(IFormParameters parameters) {
        return getReport(SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    /**
     * Чтобы не ретраить too_complicated запрос
     */
    @Step("Запросить отчет по когортному анализу и получить ошибку")
    @ParallelExecution(ALLOW)
    public V1CohortAnalysisGETSchema getReportAndExpectError(IFormParameters parameters, IExpectedError error) {
        return getReport(ERROR_MESSAGE, expectError(error), parameters);
    }

    /**
     * Мы проверяем, что запрос слишком сложный, ретраи нужно выключить
     */
    @Step("Запросить отчет по когортному анализу и получить ошибку")
    @ParallelExecution(RESTRICT)
    public V1CohortAnalysisGETSchema getReportAndExpectErrorWithoutRetry(IFormParameters parameters,
                                                                         IExpectedError error) {
        return getReportWithoutRetry(ERROR_MESSAGE, expectError(error), parameters);
    }

    @Step("Получить проценты партнера {0} с помощью группировки данных по партнеру")
    @ParallelExecution(RESTRICT)
    public List<Double> partnerPercentsFromGrouping(Long partnerId, IFormParameters parameters) {
        final CAResponse response = getReport(SUCCESS_MESSAGE, expectSuccess(),
                parameters, new CohortAnalysisParameters().withCohortType(CACohortType.partner())
        ).getCohortAnalysisData();

        final CARow partnerRow = response.getTable().stream()
                .filter(r -> r.getCohort().getId().equals(partnerId.toString()))
                .findAny()
                .orElseThrow(() -> new AssumptionException(format("Partner %s line should exist", partnerId)));

        return partnerRow.getRow().stream()
                .map(CACell::getPercent)
                .collect(Collectors.toList());
    }

    @Step("Получить проценты партнера {0} с помощью фильтра по партнеру")
    @ParallelExecution(RESTRICT)
    public List<Double> partnerPercentsFromBucketTotals(Long partnerId, IFormParameters... parameters) {
        final CAResponse response = getReport(SUCCESS_MESSAGE, expectSuccess(), aggregate(parameters),
                new CohortAnalysisParameters()
                        .withCohortType(CACohortType.installationDate())
                        .withFilter(partnerFilter(partnerId)))
                .getCohortAnalysisData();

        return response.getBucketTotals().stream()
                .map(CACell::getPercent)
                .collect(Collectors.toList());
    }

    @Step("Получить размер когорты, соответствующей партнеру {0}")
    @ParallelExecution(RESTRICT)
    public Long partnerTotalsFromGrouping(Long partnerId, IFormParameters... parameters) {
        final CAResponse response = getReport(SUCCESS_MESSAGE, expectSuccess(),
                aggregate(parameters), new CohortAnalysisParameters().withCohortType(CACohortType.partner())
        ).getCohortAnalysisData();

        final CACohortTotals totals = response.getCohortTotals().stream()
                .filter(t -> t.getCohort().getId().equals(partnerId.toString()))
                .findAny()
                .orElseThrow(() -> new AssumptionException(format("Partner %s cohort should exist", partnerId)));

        return totals.getTotals();
    }

    @Step("Получить сумму когорт с фильтром по партнеру {0}")
    @ParallelExecution(RESTRICT)
    public Long partnerPercentsFromFilter(Long partnerId, CohortAnalysisParameters parameters) {
        final CAResponse response = getReport(SUCCESS_MESSAGE, expectSuccess(),
                parameters, new CohortAnalysisParameters()
                        .withCohortType(CACohortType.installationDate())
                        .withFilter(partnerFilter(partnerId)))
                .getCohortAnalysisData();

        return response.getTotals();
    }

    private String partnerFilter(long partnerId) {
        return "ym:i:publisher==" + partnerId;
    }

    private V1CohortAnalysisGETSchema getReport(String message, Matcher matcher, IFormParameters... parameters) {
        V1CohortAnalysisGETSchema result = get(V1CohortAnalysisGETSchema.class,
                "/v1/cohort/analysis",
                aggregate(parameters));

        assertThat(message, result, matcher);

        return result;
    }

    private V1CohortAnalysisGETSchema getReportWithoutRetry(String message,
                                                            Matcher matcher,
                                                            IFormParameters... parameters) {
        V1CohortAnalysisGETSchema result = execute(V1CohortAnalysisGETSchema.class,
                RequestBuilder.Method.GET,
                "/v1/cohort/analysis",
                makeParameters(),
                null,
                aggregate(parameters));

        assertThat(message, result, matcher);

        return result;
    }
}
