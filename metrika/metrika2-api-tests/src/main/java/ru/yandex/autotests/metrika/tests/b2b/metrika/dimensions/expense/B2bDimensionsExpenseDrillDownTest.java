package ru.yandex.autotests.metrika.tests.b2b.metrika.dimensions.expense;

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
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("B2B - измерения по рекламным расходам, метод DRILLDOWN")
public class B2bDimensionsExpenseDrillDownTest extends BaseB2bDimensionsExpenseTest {

    @Before
    public void setup() {
        requestType = RequestTypes.DRILLDOWN;
        reportParameters = makeParameters()
                .append(commonParameters())
                .append(dateParameters())
                .append(new CommonReportParameters()
                        .withMetric(METRIC)
                        .withDimension(dimensionName)
                );
    }
}
