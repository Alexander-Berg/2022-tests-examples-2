package ru.yandex.autotests.metrika.tests.b2b.metrika.usercentric;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.USER_CENTRIC
})
@Stories({
        Requirements.Story.Report.Parameter.FILTERS,
        Requirements.Story.USER_CENTRIC,
        Requirements.Story.Report.Type.TABLE
})
@Title("B2B Table - user-centric сегментация по событиям")
public class UserCentricFiltersEventB2bTableTest extends UserCentricFiltersEventB2bTest {
    @Before
    public void setup() {
        requestType = RequestTypes.TABLE;
        dateFilterParameters = new TableReportParameters().withDate1(userCentricParamsHolder.getDate1())
                .withDate2(userCentricParamsHolder.getDate2())
                .withFilters(filter.build());
        super.reportParameters = getReportParameters();
    }
}
