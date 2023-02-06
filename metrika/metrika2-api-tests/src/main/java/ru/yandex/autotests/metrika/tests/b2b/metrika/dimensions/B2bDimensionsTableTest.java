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
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("B2B - измерения по просмотрам и визитам, метод TABLE")
public class B2bDimensionsTableTest extends BaseB2bDimensionsTest {
    @Before
    public void setup() {
        requestType = RequestTypes.TABLE;
        reportParameters = tail.append(new CommonReportParameters().withDimension(dimensionName));
    }

}
