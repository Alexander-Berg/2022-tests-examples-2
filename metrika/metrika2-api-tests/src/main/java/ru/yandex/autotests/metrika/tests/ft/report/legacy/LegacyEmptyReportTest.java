package ru.yandex.autotests.metrika.tests.ft.report.legacy;

import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_CONDITIONS_LIMIT;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 17.06.2015.
 */
@Features(Requirements.Feature.LEGACY)
@Stories({
        Requirements.Story.Report.Type.BYTIME,
        Requirements.Story.Report.Type.DRILLDOWN,
        Requirements.Story.Report.Type.TABLE})
@Title("Legacy отчеты: пустые отчеты")
public class LegacyEmptyReportTest {

    private static UserSteps user = new UserSteps();

    private static final Counter COUNTER = TEST_CONDITIONS_LIMIT;
    private static final String PRESET = "robot_types";
    private static final String START_DATE = "2015-01-01";
    private static final String END_DATE = "2015-01-02";

    @Test
    public void emptyTableReportTest() {
        StatV1DataGETSchema result = user.onLegacyReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withId(COUNTER.get(ID))
                        .withPreset(PRESET)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE));

        assertThat("отчет не содержит данных", result.getData(), empty());
    }

    @Test
    public void emptyByTimeReportTest() {
        StatV1DataBytimeGETSchema result = user.onLegacyReportSteps().getBytimeReportAndExpectSuccess(
                new BytimeReportParameters()
                        .withId(COUNTER.get(ID))
                        .withPreset(PRESET)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE));

        assertThat("отчет не содержит данных", result.getData(), empty());

    }

}
