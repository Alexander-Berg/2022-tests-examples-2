package ru.yandex.autotests.metrika.tests.b2b.metrika.metrics.expense;

import org.junit.Before;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;

@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.EXPENSES
})
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.METRICS})
@Title("B2B - метрики по рекламным расходам, метод BY_TIME")
public class B2bMetricsExpenseByTimeTest extends BaseB2bMetricsExpenseTest {

    @Before
    public void setup() {
        requestType = RequestTypes.BY_TIME;
        reportParameters = makeParameters()
                .append(commonParameters())
                .append(dateParameters())
                .append(goalIdParameters())
                .append(new CommonReportParameters()
                        .withDimension(DIMENSION)
                        .withMetric(metricName)
                );
    }
}
