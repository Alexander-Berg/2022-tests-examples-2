package ru.yandex.autotests.metrika.tests.b2b.metrika.presets.expense;

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
@Stories({Requirements.Story.Report.Type.COMPARISON, Requirements.Story.Report.Parameter.PRESET})
@Title("B2B - пресеты по рекламным расходам, метод COMPARISON")
public class B2BPresetsExpenseComparisonTest extends BaseB2bExpensePresetsTest {

    @Before
    public void setup() {
        requestType = RequestTypes.COMPARISON;
        reportParameters = makeParameters()
                .append(commonParameters())
                .append(comparisonDateParameters())
                .append(new CommonReportParameters().withPreset(preset));
    }
}
