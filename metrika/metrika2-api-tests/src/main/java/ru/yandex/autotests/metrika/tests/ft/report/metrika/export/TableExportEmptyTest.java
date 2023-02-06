package ru.yandex.autotests.metrika.tests.ft.report.metrika.export;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by konkov on 29.09.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.Format.XLSX,
        Requirements.Story.Report.Format.CSV
})
@Title("Отчет 'таблица': экспорт в xlsx и csv, пустой отчет")
@Issue("METR-18065")
public class TableExportEmptyTest {

    private static final Counter COUNTER = CounterConstants.NO_DATA;

    private static final String START_DATE = "2015-09-01";
    private static final String END_DATE = "2015-09-02";

    private static final String METRIC_NAME = "ym:s:visits";

    private static UserSteps user;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
    }

    @Before
    public void setup() {
        StatV1DataGETSchema result = user.onReportSteps().getTableReportAndExpectSuccess(getReportParameters());

        assumeThat("отчет данных не содержит", result.getData(), empty());
    }

    @Test
    public void checkExportXlsx() {
        user.onReportSteps().getXlsxReportAndExpectSuccess(getReportParameters());
    }

    @Test
    public void checkExportCsv() {
        user.onReportSteps().getCsvReportAndExpectSuccess(getReportParameters());
    }

    private IFormParameters getReportParameters() {
        return new TableReportParameters()
                .withId(COUNTER.get(ID))
                .withMetric(METRIC_NAME)
                .withDate1(START_DATE)
                .withDate2(END_DATE);
    }
}
