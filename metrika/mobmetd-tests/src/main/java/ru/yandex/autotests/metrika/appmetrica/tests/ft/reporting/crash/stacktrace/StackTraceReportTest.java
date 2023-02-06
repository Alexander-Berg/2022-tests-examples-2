package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.crash.stacktrace;

import com.google.common.collect.ImmutableList;
import org.hamcrest.Matchers;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.StackTraceReportParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Map;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnResponse;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.randomUrlAddress;

@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.Crash.STACKTRACE
})
@Title("Получение списка стектрейсов креша")
@RunWith(Parameterized.class)
public class StackTraceReportTest {

    private static final UserSteps testingSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    @Parameterized.Parameter
    public Application application;

    @Parameterized.Parameter(1)
    public String date;

    @Parameterized.Parameter(2)
    public String operatingSystem;

    private String crashGroupId;

    private String crashDeviceId;

    private String crashEventId;

    @Parameterized.Parameters(name = "AppId: {0}, Date: {1}, OS: {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                params(Applications.YANDEX_MUSIC, "2019-09-09", "iOS"),
                params(Applications.YANDEX_MUSIC, "2019-09-09", "android")
        );
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(application);
        loadCrashGroupId();
        loadCrashEventId();
    }

    @Test
    public void checkStackTraceReportLoads() {
        testingSteps.onStackTraceReportSteps().getStackTraceReport(new StackTraceReportParameters()
                .withAppId(application.get(Application.ID))
                .withDate(date)
                .withDeviceId(crashDeviceId)
                .withEventId(crashEventId));
    }

    @Test
    public void checkTxtStackTraceReportLoads() {
        testingSteps.onStackTraceReportSteps().getStackTraceReportTxt(new StackTraceReportParameters()
                .withAppId(application.get(Application.ID))
                .withDate(date)
                .withDeviceId(crashDeviceId)
                .withEventId(crashEventId));
    }

    @Test
    public void checkTxtStackTraceReportLoadsWithURL() {
        testingSteps.onStackTraceReportSteps().getStackTraceReportTxt(new StackTraceReportParameters()
                .withAppId(application.get(Application.ID))
                .withDate(date)
                .withDeviceId(crashDeviceId)
                .withEventId(crashEventId)
                .withUrl(randomUrlAddress()));
    }

    private void loadCrashGroupId() {
        StatV1DataGETSchema crashGroups = testingSteps.onReportSteps()
                .getTableReport(new TableReportParameters()
                        .withDimension("ym:cr2:crashGroupObj")
                        .withMetric("ym:cr2:crashes")
                        .withId(application)
                        .withFilters(format("crashGroupObj!=0 AND operatingSystem=='%s'", operatingSystem))
                        .withAccuracy("1")
                        .withDate1(date)
                        .withDate2(date)
                        .withLimit(1));

        assumeOnResponse(crashGroups);

        crashGroupId = crashGroups.getData()
                .get(0)
                .getDimensions()
                .get(0)
                .get("id");
        assumeThat("id креш-группы присутствует", crashGroupId, Matchers.notNullValue());
    }

    private void loadCrashEventId() {
        StatV1DataGETSchema crashGroups = testingSteps.onReportSteps()
                .getTableReport(new TableReportParameters()
                        .withDimension("ym:cr2:crashEventObj")
                        .withMetric("ym:cr2:crashes")
                        .withId(application)
                        .withFilters(format("crashGroupObj==%s", crashGroupId))
                        .withAccuracy("1")
                        .withDate1(date)
                        .withDate2(date)
                        .withLimit(1));

        assumeOnResponse(crashGroups);

        Map<String, String> fields = crashGroups.getData()
                .get(0)
                .getDimensions()
                .get(0);

        crashDeviceId = fields.get("appmetrica_device_id");
        assumeThat("appmetrica_device_id присутствует", crashDeviceId, Matchers.notNullValue());

        crashEventId = fields.get("id");
        assumeThat("id события присутствует", crashEventId, Matchers.notNullValue());
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    private static Object[] params(Object... params) {
        return params;
    }

}
