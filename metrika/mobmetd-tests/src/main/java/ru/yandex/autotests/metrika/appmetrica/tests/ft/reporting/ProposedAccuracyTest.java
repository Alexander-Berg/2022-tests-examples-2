package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting;

import org.hamcrest.Matcher;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonReportParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.UserAcquisitionParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;

@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.SAMPLING,
        Requirements.Story.TRAFFIC_SOURCES,
        Requirements.Story.METRICS
})
@Title("Флажок нестрогого семплирования proposedAccuracy")
public final class ProposedAccuracyTest {

    private static final UserSteps steps = UserSteps.onTesting(SUPER_LIMITED);

    /**
     * Выбираем что-то очень маленькое
     */
    private static final long appId = Applications.PUSH_SAMPLE.get(ID);

    private static final String INSANE_SAMPLING = "0.001";

    private static final CommonReportParameters STAT_PARAMS = new TableReportParameters()
            .withId(appId)
            .withDate1("today")
            .withDate2("today")
            .withMetric("ym:ge:users")
            .withAccuracy(INSANE_SAMPLING)
            .withProposedAccuracy(true);

    private static final CommonReportParameters UA_PARAMS = new UserAcquisitionParameters()
            .withId(appId)
            .withDate1("today")
            .withDate2("today")
            .withAccuracy(INSANE_SAMPLING)
            .withDimension("publisher")
            .withMetric("devices")
            .withProposedAccuracy(true);

    private static final CommonReportParameters PROFILES_PARAMS = new TableReportParameters()
            .withId(appId)
            .withDate1("today")
            .withDate2("today")
            .withDimension("ym:p:device")
            .withMetric("ym:p:users")
            .withAccuracy(INSANE_SAMPLING)
            .withProposedAccuracy(true);

    @Before
    public void setup() {
        setCurrentLayerByApp(appId);
    }

    @Test
    public void testStatV1Data() {
        StatV1DataGETSchema tableReport = steps.onReportSteps().getTableReport(STAT_PARAMS);
        assertThat("семплирование сбросилось в 100%", tableReport, notSampleable());
    }

    @Test
    public void testStatV1Bytime() {
        StatV1DataBytimeGETSchema bytimeReport = steps.onReportSteps().getByTimeReport(STAT_PARAMS);
        assertThat("семплирование сбросилось в 100%", bytimeReport, notSampleable());
    }

    @Test
    public void testStatV1Drilldown() {
        StatV1DataDrilldownGETSchema drilldownReport = steps.onReportSteps().getDrillDownReport(STAT_PARAMS);
        assertThat("семплирование сбросилось в 100%", drilldownReport, notSampleable());
    }

    @Test
    public void testUserAcquisition() {
        V2UserAcquisitionGETSchema uaReport = steps.onTrafficSourceSteps().getReport(UA_PARAMS);
        assertThat("семплирование сбросилось в 100%", uaReport, allOf(
                hasProperty("sampleable", equalTo(false)),
                hasProperty("sampleShare", equalTo(1.0d))
        ));
    }

    @Test
    public void testStatV1Profiles() {
        StatV1ProfilesGETSchema profilesReport = steps.onProfileSteps().getReport(PROFILES_PARAMS);
        assertThat("семплирование сбросилось в 100%", profilesReport, notSampleable());
    }

    @Test
    public void testStatV1ProfilesList() {
        StatV1DataGETSchema profilesList = steps.onProfileSteps().getListReport(PROFILES_PARAMS);
        assertThat("семплирование сбросилось в 100%", profilesList, notSampleable());
    }

    private static <T> Matcher<T> notSampleable() {
        return allOf(
                hasProperty("sampleable", equalTo(false)),
                hasProperty("sampled", equalTo(false)),
                hasProperty("sampleShare", equalTo(1.0d))
        );
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }
}
