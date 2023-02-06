package ru.yandex.autotests.metrika.tests.ft.report.metrika.export.conversionrate;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.empty;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

/**
 * Created by sourx on 19.05.2016.
 */
@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.Format.XLSX,
        Requirements.Story.Report.Format.CSV
})
@Title("Отчет 'Конверсии': экспорт в xlsx и csv, пустой отчет")
public class TableExportConversionRateEmptyTest {
    private final Counter COUNTER = CounterConstants.NO_DATA;
    private final String START_DATE = "2016-04-20";
    private final String END_DATE = "2016-05-19";
    private final List<String> METRICS = asList("ym:s:goalDimensionInternalReaches", "ym:s:sumVisits");
    private final String DIMENSION = "ym:s:goalDimension";

    protected UserSteps user;

    @Before
    public void setup() {
        user = new UserSteps();
        StatV1DataGETSchema result = user.onReportSteps().getTableReportAndExpectSuccess(getReportParameters());

        assumeThat("отчет данных не содержит", result.getData(), empty());
    }

    @Test
    public void checkExportXlsx() {
        user.onReportSteps().getXlsxConversionRateReportAndExpectSuccess(getExportReportParameters());
    }

    @Test
    public void checkExportCsv() {
        user.onReportSteps().getCsvConversionRateReportAndExpectSuccess(getExportReportParameters());
    }

    protected IFormParameters getReportParameters() {
        return new TableReportParameters()
                .withId(COUNTER.get(ID))
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withMetrics(METRICS)
                .withDimension(DIMENSION)
                .withAccuracy("0.1");
    }

    protected IFormParameters getExportReportParameters() {
        return new TableReportParameters()
                .withId(COUNTER)
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withAccuracy("0.1");
    }
}
