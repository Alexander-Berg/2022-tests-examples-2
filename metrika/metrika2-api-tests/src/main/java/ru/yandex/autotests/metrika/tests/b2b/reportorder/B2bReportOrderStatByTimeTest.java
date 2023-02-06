package ru.yandex.autotests.metrika.tests.b2b.reportorder;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataBytimeGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataCsvSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataXlsxSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.reportorder.ReportOrderByTimeReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest.getIgnore;
import static ru.yandex.autotests.metrika.tests.b2b.reportorder.B2bReportOrderStatTestData.REPORT_ORDER_WITH_DATA_COUNTER;
import static ru.yandex.autotests.metrika.tests.b2b.reportorder.B2bReportOrderStatTestData.REPORT_ORDER_WITH_DATA_EXECUTION_ID;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.Report.REPORT_ORDER)
@Title("B2B - Заказанные отчеты: получение построенных заказанных отчетов по времени")
@RunWith(Parameterized.class)
public class B2bReportOrderStatByTimeTest {

    private static final UserSteps userOnTest = new UserSteps();
    private static final UserSteps userOnRef = new UserSteps().useReference();

    @Parameterized.Parameters(name = "Параметры: {0}")
    public static Collection<Object[]> getParameters() {
        return of(
                toArray(new ReportOrderByTimeReportParameters()),
                toArray(new ReportOrderByTimeReportParameters()
                        .withTopKeys(3)
                ),
                toArray(new ReportOrderByTimeReportParameters()
                        .withRowIds(of(of("organic", "organic.yandex"), of("organic", "organic.google")))
                ),
                toArray(new ReportOrderByTimeReportParameters()
                        .withMetrics(of("ym:s:goal<goal_id>reaches", "ym:s:goal<goal_id>visits"))
                )
        );
    }

    @Parameterized.Parameter
    public ReportOrderByTimeReportParameters parameters;

    @Test
    public void testReport() {
        InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataBytimeGETSchema testingReport = getReport(userOnTest);
        InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataBytimeGETSchema referenceReport = getReport(userOnRef);

        assertThat("ответы совпадают", testingReport, beanEquivalent(referenceReport).fields(getIgnore()));
    }

    @Test
    public void testCsvReport() {
        List<List<String>> testingData = getCsvData(userOnTest);
        List<List<String>> referenceData = getCsvData(userOnRef);

        assertThat("ответы совпадают", testingData, beanEquivalent(referenceData));
    }

    @Test
    public void testXlsxReport() {
        List<List<String>> testingData = getXlsxData(userOnTest);
        List<List<String>> referenceData = getXlsxData(userOnRef);

        assertThat("ответы совпадают", testingData, beanEquivalent(referenceData));
    }

    private InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataBytimeGETSchema getReport(UserSteps user) {
        return user.onReportOrderStatSteps()
                .getByTimeReport(REPORT_ORDER_WITH_DATA_COUNTER.get(Counter.ID), REPORT_ORDER_WITH_DATA_EXECUTION_ID, parameters);
    }

    private List<List<String>> getCsvData(UserSteps user) {
        StatV1DataCsvSchema report = user.onReportOrderStatSteps()
                .getCsvByTimeReport(REPORT_ORDER_WITH_DATA_COUNTER.get(Counter.ID), REPORT_ORDER_WITH_DATA_EXECUTION_ID, parameters);
        return user.onResultSteps().getDimensionsAndMetricsFromCsv(report);
    }

    private List<List<String>> getXlsxData(UserSteps user) {
        StatV1DataXlsxSchema report = user.onReportOrderStatSteps()
                .getXlsxByTimeReport(REPORT_ORDER_WITH_DATA_COUNTER.get(Counter.ID), REPORT_ORDER_WITH_DATA_EXECUTION_ID, parameters);
        return user.onResultSteps().getDimensionsAndMetricsFromXlsx(report);
    }
}
