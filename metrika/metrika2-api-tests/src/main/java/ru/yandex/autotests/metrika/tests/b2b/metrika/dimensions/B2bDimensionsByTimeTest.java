package ru.yandex.autotests.metrika.tests.b2b.metrika.dimensions;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

/**
 * Created by omaz on 12.12.14.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.BYTIME, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("B2B - измерения по просмотрам и визитам, метод BY_TIME")
public class B2bDimensionsByTimeTest extends BaseB2bDimensionsTest {
    @Before
    public void setup() {
        requestType = RequestTypes.BY_TIME;
        reportParameters = tail.append(new CommonReportParameters().withDimension(dimensionName));
    }
}
