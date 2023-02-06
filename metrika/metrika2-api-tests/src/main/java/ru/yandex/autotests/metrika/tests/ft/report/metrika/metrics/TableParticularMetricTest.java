package ru.yandex.autotests.metrika.tests.ft.report.metrika.metrics;

import org.junit.Test;

import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;

import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.errors.ReportError.WRONG_METRIC;

public class TableParticularMetricTest {
    protected static final UserSteps userOnTest = new UserSteps().withDefaultAccuracy();
    @Test
    public void checkDateQuantiles() {
        userOnTest.onReportSteps().getTableReportAndExpectError(WRONG_METRIC, new TableReportParameters()
                .withId(SENDFLOWERS_RU)
                .withDate1("2021-06-05")
                .withDate2("2021-06-15")
                .withMetric("ym:s:q<quantile>Date")
                .withDimension("ym:s:sourceEngine"));
    }
}
