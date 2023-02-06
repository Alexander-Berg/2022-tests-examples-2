package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting;

import org.junit.After;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.errors.ReportError;
import ru.yandex.autotests.metrika.appmetrica.parameters.CACohortType;
import ru.yandex.autotests.metrika.appmetrica.parameters.CAGroup;
import ru.yandex.autotests.metrika.appmetrica.parameters.CAMetric;
import ru.yandex.autotests.metrika.appmetrica.parameters.CohortAnalysisParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;

@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.COHORT_ANALYSIS)
@Title("Когортный анализ (негативный)")
public class CAReportQueryNegativeTest {

    private static final UserSteps user = UserSteps.onTesting(Users.SUPER_LIMITED);

    @Test
    public void tooComplicatedTest() {
        Application app = Applications.ANDROID_BROWSER;
        CohortAnalysisParameters parameters = new CohortAnalysisParameters()
                .withId(app)
                .withAccuracy("1")
                .withDate1("2021-04-01")
                .withDate2("2021-04-10")
                .withMetric(CAMetric.EVENTS)
                .withCohortType(CACohortType.trackerParam("click_id"))
                .withMinCohortSize(1)
                .withGroup(CAGroup.DAY);
        setCurrentLayerByApp(app);
        user.onCohortAnalysisSteps().getReportAndExpectErrorWithoutRetry(parameters, ReportError.TOO_COMPLICATED);
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }
}
