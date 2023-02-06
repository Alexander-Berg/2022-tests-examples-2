package ru.yandex.autotests.metrika.tests.ft.management.logsapi;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.ResponseContent;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.logs.LogRequest;
import ru.yandex.metrika.api.management.client.external.logs.LogRequestSource;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.httpclient.lite.core.ResponseContent.NO_CONTENT;
import static ru.yandex.autotests.metrika.tests.ft.management.logsapi.LogsApiTestData.HITS_FIELDS;
import static ru.yandex.autotests.metrika.tests.ft.management.logsapi.LogsApiTestData.VISITS_FIELDS;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.metrika.api.management.client.external.logs.LogRequestSource.HITS;
import static ru.yandex.metrika.api.management.client.external.logs.LogRequestSource.VISITS;
import static ru.yandex.metrika.api.management.client.external.logs.LogRequestStatus.CLEANED_BY_USER;
import static ru.yandex.metrika.api.management.client.external.logs.LogRequestStatus.PROCESSED;

@Features(Requirements.Feature.MANAGEMENT)
@Stories({Requirements.Story.Management.LOGS_API})
@Title("Интеграционный тест на создание загрузки Logs API")
@RunWith(Parameterized.class)
public class LogsApiIntegrationTest {

    protected static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static Long SENDFLOWERS = Counters.SENDFLOWERS_RU.getId();

    private static LogRequest logRequest;
    private static LogRequest logRequestCleaned;
    private static Long logRequestId;
    private static Long logRequestPartNumber;
    private static ResponseContent response;

    @Parameterized.Parameter(0)
    public String date1;

    @Parameterized.Parameter(1)
    public String date2;

    @Parameterized.Parameter(2)
    public LogRequestSource source;

    @Parameterized.Parameter(3)
    public String fields;

    @Parameterized.Parameters(name = "Период с {0} по {1}, {2}")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(new Object[][]{
                {"2021-01-21","2021-01-21", VISITS, VISITS_FIELDS},
                {"2021-01-21","2021-01-21", HITS, HITS_FIELDS}
        });
    }

    @Before
    public void setup() {
        logRequestId = user.onManagementSteps().onLogsApiSteps()
                .createLogRequest(SENDFLOWERS, date1, date2, source, fields).getRequestId();
        user.onManagementSteps().onLogsApiSteps().waitForLogRequestProcessing(SENDFLOWERS, logRequestId);
        logRequest = user.onManagementSteps().onLogsApiSteps().getLogRequest(SENDFLOWERS, logRequestId);

        logRequestPartNumber = logRequest.getParts().get(0).getPartNumber();
        response = user.onManagementSteps().onLogsApiSteps().download(SENDFLOWERS, logRequestId, logRequestPartNumber);

        logRequestCleaned = user.onManagementSteps().onLogsApiSteps().clean(SENDFLOWERS, logRequestId);
    }

    @Test
    public void logRequestProcessingTest() {
        assertThat("запрос обработался", logRequest.getStatus(), equalTo(PROCESSED));
    }

    @Test
    public void logRequestDownloadTest() {
        assertThat("загрузка logs api скачалась", response, not(equalTo(NO_CONTENT)));
    }

    @Test
    public void logRequestCleanTest() {
        assertThat("загрузка была удалена пользователем", logRequestCleaned.getStatus(), equalTo(CLEANED_BY_USER));
    }
}
