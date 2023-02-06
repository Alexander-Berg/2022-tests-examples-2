package ru.yandex.autotests.metrika.tests.ft.management.logsapi;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.httpclient.lite.core.ResponseContent;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.logs.LogRequest;
import ru.yandex.metrika.api.management.client.external.logs.LogRequestSource;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.STAT_MTRS;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPPORT;
import static ru.yandex.autotests.metrika.utils.AllureUtils.*;
import static ru.yandex.metrika.api.management.client.external.logs.LogRequestStatus.PROCESSED;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.LOGS_API)
@Title("Logs api: получение заказов логов, проверка формата")
public class LogsApiFormatTest {

    private static final Long COUNTER_ID = STAT_MTRS.getId();
    private static UserSteps user = new UserSteps().withUser(SUPPORT);

    private static LogRequest logRequest;
    private static Long logRequestId;
    private static List<Map<String, String>> rows;
    private static List<CSVRecord> recordsCsv;
    private static List<String[]> recordsClickHouse;
    private static ResponseContent contentCsv;
    private static ResponseContent contentClickHouse;

    @BeforeClass
    public static void init() {
        logRequestId = user.onManagementSteps().onLogsApiSteps().createLogRequest(COUNTER_ID, "2018-02-01",
                "2018-02-01", LogRequestSource.VISITS, LogsApiTestData.VISITS_TIME_AND_PARAMS).getRequestId();
        user.onManagementSteps().onLogsApiSteps().waitForLogRequestProcessing(COUNTER_ID, logRequestId);
        logRequest = user.onManagementSteps().onLogsApiSteps().getLogRequest(COUNTER_ID, logRequestId);

        assumeThat("дождались обработки запроса логов и получили его", logRequest.getStatus(), equalTo(PROCESSED));

        contentCsv = user.onManagementSteps().onLogsApiSteps().download(logRequest.getCounterId(),
                logRequest.getRequestId(), logRequest.getParts().get(0).getPartNumber());
        recordsCsv = Collections.emptyList();
        try {
            CSVParser parser = new CSVParser(new InputStreamReader(contentCsv.asStream()),
                    CSVFormat.RFC4180.withDelimiter('\t').withHeader());
            recordsCsv = parser.getRecords();
        } catch (Exception e) {
            addTextAttachment("error", e.toString());
            assumeThat("удалось распарсить ответ", false, is(true));
        }

        rows = recordsCsv.stream().map(CSVRecord::toMap).collect(Collectors.toList());

        contentClickHouse = user.onManagementSteps().onLogsApiSteps().download(logRequest.getCounterId(),
                logRequest.getRequestId(), logRequest.getParts().get(0).getPartNumber(), "clickhouse");
        recordsClickHouse = new BufferedReader(new InputStreamReader(contentClickHouse
                .asStream())).lines().skip(1).map(l -> l.split("\t")).collect(Collectors.toList());
    }

    @Test
    public void checkParamsArray() {
        assumeThat("записи есть", recordsCsv, not(empty()));
        assertThat("в параметрах - массив", rows,
                everyItem(hasEntry(is("ym:s:params"), allOf(startsWith("["), endsWith("]")))));
    }

    @Test
    public void checkCsvFormat() {
        assumeThat("записи есть", recordsCsv, not(empty()));
        assertThat("есть строка с Q'n'A и знаками", rows,
                hasItem(hasEntry(is("ym:s:params"), allOf(startsWith("["), endsWith("]"),
                        containsString("'{\"Q\\'n\\'A\":{\"001\":{\"Процент\":\"1\\t23\\\\n4\"}}}'")))));
    }

    @Test
    public void checkClickHouseFormat() {
        assumeThat("записи есть", recordsClickHouse, not(empty()));
        assertThat("в параметрах - массив", recordsClickHouse,
                everyItem(array(notNullValue(), allOf(startsWith("["), endsWith("]"), not(contains("\"\""))))));
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onLogsApiSteps().clean(COUNTER_ID, logRequest.getRequestId());
    }
}
