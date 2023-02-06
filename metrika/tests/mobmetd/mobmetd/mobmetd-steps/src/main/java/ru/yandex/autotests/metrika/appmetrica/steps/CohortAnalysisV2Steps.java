package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;

import org.hamcrest.Matcher;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataCohortGETSchema;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.api.cohort.response.model.CAResponse;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.aggregate;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class CohortAnalysisV2Steps extends AppMetricaBaseSteps {
    public CohortAnalysisV2Steps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить отчет по когортному анализу")
    @ParallelExecution(RESTRICT)
    public CAResponse getReport(IFormParameters parameters) {
        return getReport(SUCCESS_MESSAGE, expectSuccess(), parameters).getCohortAnalysisData();
    }

    private StatV1DataCohortGETSchema getReport(String message, Matcher matcher, IFormParameters... parameters) {
        StatV1DataCohortGETSchema result = get(StatV1DataCohortGETSchema.class,
                "/stat/v1/data/cohort",
                aggregate(parameters));

        assertThat(message, result, matcher);

        return result;
    }

}
