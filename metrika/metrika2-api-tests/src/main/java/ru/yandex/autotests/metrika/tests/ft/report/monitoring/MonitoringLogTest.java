package ru.yandex.autotests.metrika.tests.ft.report.monitoring;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.MonitoringLogParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.constructor.monitoring.MonIntervalExternal;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчик: получение лога мониторинга")
public class MonitoringLogTest {

    private static final long COUNTER_ID = Counters.YANDEX_METRIKA_2_0.getId();
    private static final IFormParameters PARAMS = new MonitoringLogParameters()
            .withDate1("2019-06-24")
            .withDate2("2019-06-25")
            .withId(COUNTER_ID)
            .withSort("domain");
    private static final List<MonIntervalExternal> EXPECTED_LOG = asList(
            new MonIntervalExternal().withDomain("metrica.yandex.com").withFrom("2019-06-24T00:00:00+03:00").withTo("2019-06-26T00:00:00+03:00").withLength(172800L).withHttpCode(200L).withStatus("alive").withMessage("OK"),
            new MonIntervalExternal().withDomain("metrica.yandex.com.tr").withFrom("2019-06-24T00:00:00+03:00").withTo("2019-06-26T00:00:00+03:00").withLength(172800L).withHttpCode(200L).withStatus("alive").withMessage("OK"),
            new MonIntervalExternal().withDomain("metrika.yandex.by").withFrom("2019-06-24T00:00:00+03:00").withTo("2019-06-26T00:00:00+03:00").withLength(172800L).withHttpCode(200L).withStatus("alive").withMessage("OK"),
            new MonIntervalExternal().withDomain("metrika.yandex.kz").withFrom("2019-06-24T00:00:00+03:00").withTo("2019-06-26T00:00:00+03:00").withLength(172800L).withHttpCode(200L).withStatus("alive").withMessage("OK"),
            new MonIntervalExternal().withDomain("metrika.yandex.ru").withFrom("2019-06-24T00:00:00+03:00").withTo("2019-06-26T00:00:00+03:00").withLength(172800L).withHttpCode(200L).withStatus("alive").withMessage("OK"),
            new MonIntervalExternal().withDomain("metrika.yandex.ua").withFrom("2019-06-24T00:00:00+03:00").withTo("2019-06-26T00:00:00+03:00").withLength(172800L).withHttpCode(200L).withStatus("alive").withMessage("OK"),
            new MonIntervalExternal().withDomain("webvisor.com").withFrom("2019-06-24T00:00:00+03:00").withTo("2019-06-26T00:00:00+03:00").withLength(172800L).withHttpCode(200L).withStatus("alive").withMessage("OK")
    );

    private List<MonIntervalExternal> data;

    @Before
    public void setUp() {
        data = new UserSteps().onReportSteps().getMonitoringLogAndExpectSuccess(PARAMS).getData();
    }

    @Test
    public void checkMonitoringLog() {
        assertThat("лог мониторинга совпадает с ожидаемым", data, equalTo(EXPECTED_LOG));
    }
}
