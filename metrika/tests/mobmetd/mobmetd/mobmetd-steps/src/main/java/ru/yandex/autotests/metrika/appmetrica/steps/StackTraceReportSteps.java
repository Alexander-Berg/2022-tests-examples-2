package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.httpclientlite.core.Response;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.V1CrashesStacktraceGETSchema;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.mobmet.crash.response.stacktrace.StackTraceReport;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.httpclientlite.core.RequestBuilder.Method.GET;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.aggregate;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class StackTraceReportSteps extends AppMetricaBaseSteps {

    public StackTraceReportSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить стектрейс креша")
    @ParallelExecution(RESTRICT)
    public StackTraceReport getStackTraceReport(IFormParameters... parameters) {
        return getStackTraceReport(SUCCESS_MESSAGE, expectSuccess(), parameters).getResponse();
    }

    @Step("Получить стектрейс креша в текстовом виде")
    @ParallelExecution(RESTRICT)
    public String getStackTraceReportTxt(IFormParameters... parameters) {
        return getStackTraceReportTxt(SUCCESS_MESSAGE, 200, parameters);
    }

    private V1CrashesStacktraceGETSchema getStackTraceReport(String message,
                                                             Matcher matcher,
                                                             IFormParameters... parameters) {
        V1CrashesStacktraceGETSchema result = get(
                V1CrashesStacktraceGETSchema.class,
                "/v1/crashes/stacktrace",
                aggregate(parameters)
        );
        assertThat(message, result, matcher);
        return result;
    }

    private String getStackTraceReportTxt(String message,
                                          int expectedCode,
                                          IFormParameters... parameters) {
        Response response = execute(GET, "/v1/crashes/stacktrace.txt", makeParameters(), null, parameters);
        assertThat(message, response.getStatusLine().getStatusCode(), equalTo(expectedCode));
        return response.getResponseContent().asString();
    }

}
