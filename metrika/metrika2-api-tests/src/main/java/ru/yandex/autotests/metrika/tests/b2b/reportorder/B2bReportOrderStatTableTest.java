package ru.yandex.autotests.metrika.tests.b2b.reportorder;

import org.hamcrest.Matcher;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataCsvSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataXlsxSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.reportorder.ReportOrderTableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest.getIgnore;
import static ru.yandex.autotests.metrika.tests.b2b.reportorder.B2bReportOrderStatTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.Report.REPORT_ORDER)
@Title("B2B - Заказанные отчеты: получение построенных заказанных отчетов")
@RunWith(Parameterized.class)
public class B2bReportOrderStatTableTest {

    private static final UserSteps userOnTest = new UserSteps();
    private static final UserSteps userOnRef = new UserSteps().useReference();

    @Parameterized.Parameters(name = "Параметры: {0}")
    public static Collection<Object[]> getParameters() {
        return of(
                toArray(new ReportOrderTableReportParameters(), iterableWithSize(greaterThan(0))),
                toArray(new ReportOrderTableReportParameters().withLimit(10), iterableWithSize(10)),
                toArray(new ReportOrderTableReportParameters().withOffset(11).withLimit(10), iterableWithSize(10))
        );
    }

    @Parameterized.Parameter
    public ReportOrderTableReportParameters parameters;

    @Parameterized.Parameter(1)
    public Matcher matcher;

    @Test
    public void testReport() {
        InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataGETSchema testingReport = getReport(userOnTest);
        InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataGETSchema referenceReport = getReport(userOnRef);

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

    private InternalStatV1CounterCounterIdReportExecutionReportExecutionIdDataGETSchema getReport(UserSteps user) {
        return user.onReportOrderStatSteps()
                .getTableReport(REPORT_ORDER_WITH_DATA_COUNTER.get(Counter.ID), REPORT_ORDER_WITH_DATA_EXECUTION_ID, parameters);
    }

    private List<List<String>> getCsvData(UserSteps user) {
        StatV1DataCsvSchema report = user.onReportOrderStatSteps()
                .getCsvTableReport(REPORT_ORDER_WITH_DATA_COUNTER.get(Counter.ID), REPORT_ORDER_WITH_DATA_EXECUTION_ID, parameters);
        return user.onResultSteps().getDimensionsAndMetricsFromCsv(report);
    }

    private List<List<String>> getXlsxData(UserSteps user) {
        StatV1DataXlsxSchema report = user.onReportOrderStatSteps()
                .getXlsxTableReport(REPORT_ORDER_WITH_DATA_COUNTER.get(Counter.ID), REPORT_ORDER_WITH_DATA_EXECUTION_ID, parameters);
        return user.onResultSteps().getDimensionsAndMetricsFromXlsx(report);
    }
}
