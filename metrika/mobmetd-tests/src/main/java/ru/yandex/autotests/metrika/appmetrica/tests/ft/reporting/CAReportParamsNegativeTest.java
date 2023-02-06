package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.errors.ReportError;
import ru.yandex.autotests.metrika.appmetrica.parameters.*;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_METRO;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CACohortType.*;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CAConversion.sessionStart;
import static ru.yandex.autotests.metrika.appmetrica.parameters.CAConversion.toEventLabel;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;


@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.COHORT_ANALYSIS)
@Title("Когортный анализ (400-ые ответы)")
@RunWith(Parameterized.class)
public final class CAReportParamsNegativeTest {

    private static final UserSteps testingSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final Application APP = YANDEX_METRO;
    private static final String SOME_EVENT_LABEL = "application.start-session";
    private static final String SOME_TRACKER_PARAM = "utm_source";

    @Parameterized.Parameter
    public CACohortType cohortType;

    @Parameterized.Parameter(1)
    public CAMetric metric;

    @Parameterized.Parameter(2)
    public CARetention retention;

    @Parameterized.Parameter(3)
    public CAGroup group;

    @Parameterized.Parameter(4)
    public CAConversion conversion;

    private IFormParameters parameters;

    @Parameterized.Parameters(name = "CohortType: {0}. Metric: {1}. Retention: {2}. Group: {3}. Conversion: {4}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(installationDate(), tracker(), partner(), trackerParam(SOME_TRACKER_PARAM))
                .values(CAMetric.EVENTS)
                .values(CARetention.CLASSIC, CARetention.ROLLING)
                .values(CAGroup.values())
                .values(sessionStart(), toEventLabel(SOME_EVENT_LABEL))
                .build();
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(APP.get(ID));
        parameters = new CohortAnalysisParameters()
                .withId(APP.get(ID))
                .withDate1(apiProperties().getCaStartDate())
                .withDate2(apiProperties().getCaEndDate())
                .withAccuracy("1")
                .withCohortType(cohortType)
                .withMetric(metric)
                .withRetention(retention)
                .withGroup(group)
                .withConversion(conversion)
                .withLang("ru")
                .withRequestDomain("ru");
    }

    @Test
    public void checkReportsMatch() {
        testingSteps.onCohortAnalysisSteps().getReportAndExpectError(parameters, ReportError.BAD_RETENTION_FILTER);
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }
}
