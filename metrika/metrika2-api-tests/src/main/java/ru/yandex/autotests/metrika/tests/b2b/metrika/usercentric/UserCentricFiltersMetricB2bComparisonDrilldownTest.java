package ru.yandex.autotests.metrika.tests.b2b.metrika.usercentric;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.USER_CENTRIC
})
@Stories({
        Requirements.Story.Report.Parameter.FILTERS,
        Requirements.Story.Report.Type.COMPARISON_DRILLDOWN,
        Requirements.Story.USER_CENTRIC})
@Title("B2B Comparison Drilldown - user-centric сегментация по метрикам")
public class UserCentricFiltersMetricB2bComparisonDrilldownTest extends UserCentricFiltersMetricB2bTest {
    @Before
    public void setup() {
        requestType = RequestTypes.COMPARISON_DRILLDOWN;
        dateFilterParameters = new ComparisonReportParameters().withDate1_a(userCentricParamsHolder.getDate1())
                .withDate1_b(userCentricParamsHolder.getDate1())
                .withDate2_a(userCentricParamsHolder.getDate2())
                .withDate2_b(userCentricParamsHolder.getDate2())
                .withFilters_a(filter.build())
                .withFilters_b(filter.build());
        super.reportParameters = getReportParameters();
    }
}
