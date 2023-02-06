package ru.yandex.autotests.metrika.tests.b2b.metrika.dimensions.advertising;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

/**
 * Created by konkov on 30.07.2015.
 */
@Features({
        Requirements.Feature.DATA,
        Requirements.Feature.ADVERTISING
})
@Stories({Requirements.Story.Report.Type.COMPARISON_DRILLDOWN, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("B2B - измерения по кликам Директа, метод COMPARISON_DRILLDOWN")
public class B2bDimensionsAdvertisingComparisonDrillDownTest extends BaseB2bDimensionsAdvertisingTest {
    @Before
    public void setup() {
        requestType = RequestTypes.COMPARISON_DRILLDOWN;
        reportParameters = tail.append(new CommonReportParameters().withDimension(dimensionName));
    }
}
