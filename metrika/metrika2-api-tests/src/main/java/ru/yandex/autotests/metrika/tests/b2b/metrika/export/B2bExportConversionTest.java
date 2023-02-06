package ru.yandex.autotests.metrika.tests.b2b.metrika.export;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

/**
 * Created by sourx on 27/06/16.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Format.XLSX,
    Requirements.Story.Report.Format.CSV})
@Title("B2B - Экспорт отчета 'Конверсии' в excel")
public class B2bExportConversionTest extends BaseB2bExportTest {
    private static final Counter COUNTER = CounterConstants.LITE_DATA;
    private static final String START_DATE = "2016-04-20";
    private static final String END_DATE = "2016-05-19";

    @Before
    public void setup() {
        requestType = RequestTypes.CONVERSION_RATE;
        reportParameters = new TableReportParameters()
                .withId(COUNTER)
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withAccuracy("0.1");
    }
}
