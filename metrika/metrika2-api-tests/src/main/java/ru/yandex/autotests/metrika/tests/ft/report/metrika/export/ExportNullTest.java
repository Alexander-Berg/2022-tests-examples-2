package ru.yandex.autotests.metrika.tests.ft.report.metrika.export;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.*;
import ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Issue;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_UPLOADINGS;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.*;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.BYTIME,
        Requirements.Story.Report.Format.XLSX,
        Requirements.Story.Report.Format.CSV
})
@Title("Отчет 'по времени': экспорт в xlsx и csv, null в отчете")
@Issue("METR-24997")
@RunWith(Parameterized.class)
public class ExportNullTest {

    private static final Counter COUNTER = TEST_UPLOADINGS;
    private static final String START_DATE = "2017-03-01";
    private static final String END_DATE = "2017-04-01";
    private static final String DIMENSION_NAME = "ym:s:datePeriod<group>";
    private static final String METRIC_NAME = "ym:s:offlineCallHoldDurationTillMissAvg";

    private static final FreeFormParameters COMMON_PARAMETERS = new FreeFormParameters()
            .append(new CommonReportParameters()
                    .withId(COUNTER)
                    .withMetric(METRIC_NAME)
                    .withAccuracy("full"))
            .append(new ParametrizationParameters()
                    .withGroup(GroupEnum.DAY));

    private UserSteps user = new UserSteps().withDefaultAccuracy();

    @Parameterized.Parameter
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                {TABLE, new TableReportParameters()
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)
                        .withDimension(DIMENSION_NAME)},
                {COMPARISON, new ComparisonReportParameters()
                        .withDate1_a(START_DATE)
                        .withDate2_a(END_DATE)
                        .withDate1_b(START_DATE)
                        .withDate2_b(END_DATE)
                        .withDimension(DIMENSION_NAME)},
                {BY_TIME, new BytimeReportParameters()
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)}
        });
    }

    @Test
    public void checkExportXlsx() {
        user.onReportSteps().getXlsxReport(requestType, COMMON_PARAMETERS, parameters);
    }

    @Test
    public void checkExportCsv() {
        user.onReportSteps().getCsvReport(requestType, COMMON_PARAMETERS, parameters);
    }
}
