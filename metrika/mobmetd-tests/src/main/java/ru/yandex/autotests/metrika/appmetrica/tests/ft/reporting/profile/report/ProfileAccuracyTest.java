package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.profile.report;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonReportParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.utils.ReportUtils;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.everyItem;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_METRO;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;

@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.QUERY
})
@Title("Семплирование должно быть равно заданному во всех запросах к Clickhouse")
public class ProfileAccuracyTest {

    private static final UserSteps steps = UserSteps.onTesting(SUPER_LIMITED);

    private static final Application APPLICATION = YANDEX_METRO;

    /**
     * Плохо что мы предполагаем как Clickhouse отформатирует запрос, но другого способа вроде как нет
     */
    private static final String ACCURACY = "0.02";

    private static final CommonReportParameters PROFILES_PARAMS = new TableReportParameters()
            .withId(APPLICATION)
            .withDate1("today")
            .withDate2("today")
            .withDimension("ym:p:regionCountry")
            .withMetric("ym:p:users,ym:p:medianDaysSinceLastVisit,ym:p:histogramUsersBySessionsCount")
            .withAccuracy(ACCURACY);

    @Before
    public void setup() {
        setCurrentLayerByApp(APPLICATION);
    }

    @Test
    public void test() {
        StatV1ProfilesGETSchema profilesReport = steps.onProfileSteps().getReport(PROFILES_PARAMS);

        UserSteps.assumeOnResponse(profilesReport);

        List<String> clickhouseQueryList = ReportUtils.collectCHQueries(profilesReport.getProfile());

        assertThat("семплирование равно заданному", clickhouseQueryList, everyItem(containsString("SAMPLE " + ACCURACY)));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }
}
