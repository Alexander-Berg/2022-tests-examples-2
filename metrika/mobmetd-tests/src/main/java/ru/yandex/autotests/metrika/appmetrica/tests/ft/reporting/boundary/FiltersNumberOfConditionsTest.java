package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.boundary;

import org.junit.After;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.*;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.stream.Collectors;
import java.util.stream.IntStream;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.errors.ReportError.TOO_MANY_TERMS_IN_FILTERS;
import static ru.yandex.autotests.metrika.appmetrica.parameters.TSSource.INSTALLATION;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

@SuppressWarnings("unchecked")
@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.Type.TABLE,
        Requirements.Story.Type.DRILLDOWN,
        Requirements.Story.Type.BYTIME
})
@Title("Количество фильтров в запросе")
public class FiltersNumberOfConditionsTest {

    private static final int CONDITIONS_LIMIT = 100;

    private final UserSteps user = UserSteps.onTesting(Users.SIMPLE_USER);

    private static final String CONDITION_DIMENSION = "device";

    private IFormParameters maximumFiltersParameters;
    private IFormParameters moreThanMaximumFiltersParameters;

    private IFormParameters maximumFiltersProfileParameters;
    private IFormParameters moreThanMaximumFiltersProfileParameters;

    private IFormParameters maximumFiltersUAParameters;
    private IFormParameters moreThanMaximumFiltersUAParameters;

    private IFormParameters maximumFiltersCAParameters;
    private IFormParameters moreThanMaximumFiltersCAParameters;

    private Long appId;

    @Before
    public void setup() {
        final Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        String maximumFilter = IntStream.range(0, CONDITIONS_LIMIT)
                .mapToObj(FiltersNumberOfConditionsTest::buildFilterUnit)
                .collect(Collectors.joining(" AND "));

        String moreThanMaximumFilter = maximumFilter + " AND " + buildFilterUnit(CONDITIONS_LIMIT);

        maximumFiltersParameters = buildCommonTableParameters(appId).withFilters(maximumFilter);
        moreThanMaximumFiltersParameters = buildCommonTableParameters(appId).withFilters(moreThanMaximumFilter);

        maximumFiltersProfileParameters = buildProfileParameters(appId).withFilters(maximumFilter);
        moreThanMaximumFiltersProfileParameters = buildProfileParameters(appId).withFilters(moreThanMaximumFilter);

        maximumFiltersUAParameters = buildUAParameters(appId).withFilters(maximumFilter);
        moreThanMaximumFiltersUAParameters = buildUAParameters(appId).withFilters(moreThanMaximumFilter);

        maximumFiltersCAParameters = buildCAParameters(appId).withFilter(maximumFilter);
        moreThanMaximumFiltersCAParameters = buildCAParameters(appId).withFilter(moreThanMaximumFilter);
    }

    @Test
    public void tableMaximumConditionsInQuery() {
        StatV1DataGETSchema result = user.onReportSteps().getTableReport(maximumFiltersParameters);
        assertThat("запрос был успешным", result, expectSuccess());
    }

    @Test
    public void tableMoreThanMaximumConditionsInQuery() {
        StatV1DataGETSchema result = user.onReportSteps().getTableReport(moreThanMaximumFiltersParameters);
        assertThat("запрос завершился с ошибкой", result, expectError(TOO_MANY_TERMS_IN_FILTERS));
    }

    @Test
    public void drilldownMaximumConditionsInQuery() {
        StatV1DataDrilldownGETSchema result = user.onReportSteps().getDrillDownReport(maximumFiltersParameters);
        assertThat("запрос был успешным", result, expectSuccess());
    }

    @Test
    public void drilldownMoreThanMaximumConditionsInQuery() {
        StatV1DataDrilldownGETSchema result = user.onReportSteps().getDrillDownReport(moreThanMaximumFiltersParameters);
        assertThat("запрос завершился с ошибкой", result, expectError(TOO_MANY_TERMS_IN_FILTERS));
    }

    @Test
    public void bytimeMaximumConditionsInQuery() {
        StatV1DataBytimeGETSchema result = user.onReportSteps().getByTimeReport(maximumFiltersParameters);
        assertThat("запрос был успешным", result, expectSuccess());
    }

    @Test
    public void bytimeMoreThanMaximumConditionsInQuery() {
        StatV1DataBytimeGETSchema result = user.onReportSteps().getByTimeReport(moreThanMaximumFiltersParameters);
        assertThat("запрос завершился с ошибкой", result, expectError(TOO_MANY_TERMS_IN_FILTERS));
    }

    @Test
    public void treeMaximumConditionsInQuery() {
        user.onReportSteps().getTree(maximumFiltersParameters);
    }

    @Test
    public void treeMoreThanMaximumConditionsInQuery() {
        user.onReportSteps().getTreeAndExpectError(moreThanMaximumFiltersParameters, TOO_MANY_TERMS_IN_FILTERS);
    }

    @Test
    public void profileMaximumConditionsInQuery() {
        StatV1ProfilesGETSchema result = user.onProfileSteps().getReport(maximumFiltersProfileParameters);
        assertThat("запрос был успешным", result, expectSuccess());
    }

    @Test
    @Ignore("MOBMET-8903")
    public void profileMoreThanMaximumConditionsInQuery() {
        StatV1ProfilesGETSchema result = user.onProfileSteps().getReport(moreThanMaximumFiltersProfileParameters);
        assertThat("запрос завершился с ошибкой", result, expectError(TOO_MANY_TERMS_IN_FILTERS));
    }

    @Test
    public void profileListMaximumConditionsInQuery() {
        StatV1DataGETSchema result = user.onProfileSteps().getListReport(maximumFiltersProfileParameters);
        assertThat("запрос был успешным", result, expectSuccess());
    }

    @Test
    @Ignore("MOBMET-8903")
    public void profileListMoreThanMaximumConditionsInQuery() {
        StatV1DataGETSchema result = user.onProfileSteps().getListReport(moreThanMaximumFiltersProfileParameters);
        assertThat("запрос завершился с ошибкой", result, expectError(TOO_MANY_TERMS_IN_FILTERS));
    }

    @Test
    public void uaMaximumConditionsInQuery() {
        V2UserAcquisitionGETSchema result = user.onTrafficSourceSteps().getReport(maximumFiltersUAParameters);
        assertThat("запрос был успешным", result, expectSuccess());
    }

    @Test
    @Ignore("MOBMET-8903")
    public void uaMoreThanMaximumConditionsInQuery() {
        V2UserAcquisitionGETSchema result = user.onTrafficSourceSteps().getReport(moreThanMaximumFiltersUAParameters);
        assertThat("запрос завершился с ошибкой", result, expectError(TOO_MANY_TERMS_IN_FILTERS));
    }

    @Test
    public void caMaximumConditionsInQuery() {
        user.onCohortAnalysisSteps().getReport(maximumFiltersCAParameters);
    }

    @Test
    @Ignore("MOBMET-8903")
    public void caMoreThanMaximumConditionsInQuery() {
        user.onCohortAnalysisSteps().getReportAndExpectError(
                moreThanMaximumFiltersCAParameters, TOO_MANY_TERMS_IN_FILTERS);
    }

    @After
    public void teardown() {
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static String buildFilterUnit(int regionId) {
        return CONDITION_DIMENSION + "==" + regionId;
    }

    private static TableReportParameters buildCommonTableParameters(Long appId) {
        TableReportParameters parameters = new TableReportParameters();
        parameters.setId(appId);
        parameters.setMetric("ym:u:users");
        parameters.setDimension("ym:u:regionCountry");
        return parameters;
    }

    private static TableReportParameters buildProfileParameters(Long appId) {
        TableReportParameters parameters = new TableReportParameters();
        parameters.setId(appId);
        parameters.setMetric("ym:p:users");
        parameters.setDimension("ym:p:regionCountry");
        return parameters;
    }

    private static UserAcquisitionParameters buildUAParameters(Long appId) {
        UserAcquisitionParameters parameters = new UserAcquisitionParameters();
        parameters.withId(appId);
        parameters.withMetric("devices");
        parameters.withDimension("campaign");
        parameters.withSource(INSTALLATION);
        return parameters;
    }

    private static CohortAnalysisParameters buildCAParameters(Long appId) {
        CohortAnalysisParameters parameters = new CohortAnalysisParameters();
        parameters.withId(appId);
        parameters.withCohortType(CACohortType.installationDate());
        parameters.withMetric(CAMetric.DEVICES);
        parameters.withRetention(CARetention.CLASSIC);
        parameters.withGroup(CAGroup.DAY);
        parameters.withDate1("today");
        parameters.withDate2("today");
        return parameters;
    }
}
