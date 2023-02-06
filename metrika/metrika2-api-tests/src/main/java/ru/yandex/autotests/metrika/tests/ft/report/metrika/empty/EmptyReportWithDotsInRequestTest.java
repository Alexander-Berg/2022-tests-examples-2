package ru.yandex.autotests.metrika.tests.ft.report.metrika.empty;

import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.Matchers.empty;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_CONDITIONS_LIMIT;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features({Requirements.Feature.REPORT, "METR-28377"})
@Stories({Requirements.Story.Report.Type.DRILLDOWN})
@Title("Отчет 'drill down': пустой отчет с точками в ID")
public class EmptyReportWithDotsInRequestTest {

    private static final Counter COUNTER = TEST_CONDITIONS_LIMIT;
    private static final String START_DATE = "2015-01-01";
    private static final String END_DATE = "2015-01-02";

    private UserSteps user;

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy();
    }

    //"METR-25697 alias"
    @Test
    public void drillDownEmptyReportWithDotsInId() {
        StatV1DataDrilldownGETSchema report = user.onReportSteps()
                .getDrilldownReportAndExpectSuccess(
                        new DrillDownReportParameters()
                                .withId(COUNTER.get(ID))
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withDimensions(of("ym:s:productVariant", "ym:s:productName"))
                                .withParentIds(of("a.b.c"))
                                .withMetric("ym:s:productImpressionsUniq")
                );

        assertThat("отчет не содержит данных", report.getData(), empty());
    }
}
