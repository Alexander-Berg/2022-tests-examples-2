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
        Requirements.Story.Report.Type.BYTIME,
        Requirements.Story.Report.Parameter.FILTERS,
        Requirements.Story.USER_CENTRIC})
@Title("B2B ByTime - user-centric сегментация по атрибутам")
public class UserCentricFiltersAttrB2bByTimeTest extends UserCentricFiltersAttrB2bTest {
    @Before
    public void setup() {
        requestType = RequestTypes.BY_TIME;
        dateFilterParameters = new TableReportParameters().withDate1(userCentricParamsHolder.getDate1())
                .withDate2(userCentricParamsHolder.getDate2())
                .withFilters(filter.build());
        super.reportParameters = getReportParameters();
    }
}
