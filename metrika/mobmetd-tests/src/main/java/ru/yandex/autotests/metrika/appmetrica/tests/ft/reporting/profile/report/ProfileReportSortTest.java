package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.profile.report;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.ProfilesReportParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.metrika.mobmet.profiles.report.ProfilesRow;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Stream;

import static java.util.Comparator.comparing;
import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.APPMETRICA_PROD;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;

@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.DIMENSIONS, Requirements.Story.METRICS
})
@Title("Сортировка в отчёте по профилям")
@RunWith(Parameterized.class)
public class ProfileReportSortTest {

    private static final Application APPLICATION = APPMETRICA_PROD;

    private static final String METRIC = "ym:p:users";

    private static final Comparator<ProfilesRow> DIMENSION_NAME_DOUBLE_COMPARATOR =
            comparing((ProfilesRow row) -> Double.parseDouble(row.getDimensions().get(0).get("name")));

    private static final Comparator<ProfilesRow> DIMENSION_NAME_STRING_COMPARATOR =
            comparing((ProfilesRow row) -> row.getDimensions().get(0).get("name"));

    private static final Comparator<ProfilesRow> METRIC_COMPARATOR =
            comparing((ProfilesRow row) -> (Double) row.getMetrics().get(0));

    private static final UserSteps onTesting = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    @Parameterized.Parameter
    public String attribute;

    @Parameterized.Parameter(1)
    public Sort sort;

    @Parameterized.Parameter(2)
    public Double intervalsLength;

    @Parameterized.Parameters(name = "Attr: {0}. Sort: {1}. IntervalsLength: {2}")
    public static Collection<Object[]> createParameters() {
        return Stream.concat(
                CombinatorialBuilder.builder()
                        .values("ym:p:customNumberAttribute1388", "ym:p:customCounterAttribute1397")
                        .values(Sort.values())
                        .values(0.0, 1.5, 2.0, null)
                        .build()
                        .stream(),
                CombinatorialBuilder.builder()
                        .values("ym:p:customStringAttribute1385")
                        .values(Sort.values())
                        .values((Double) null)
                        .build()
                        .stream()
        ).collect(toList());
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(APPLICATION);
    }

    @Test
    public void checkDimensionIsSorted() {
        StatV1ProfilesGETSchema report = onTesting.onProfileSteps().getReport(reportParams());
        List<ProfilesRow> actualRows = report.getData();
        List<ProfilesRow> expectedRows = new ArrayList<>(actualRows);
        expectedRows.sort(comparator());

        assertThat("Порядок сортировки совпадает с ожидаемым", actualRows, equivalentTo(expectedRows));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    private TableReportParameters reportParams() {
        return new ProfilesReportParameters()
                .withIntervalsLength(intervalsLength)
                .withId(APPLICATION)
                .withMetric(METRIC)
                .withLimit(50)
                .withDimension(attribute)
                .withSort(sort());
    }

    private String sort() {
        switch (sort) {
            case ASC_DIM:
                return attribute;
            case DESC_DIM:
                return "-" + attribute;
            case ASC_METRIC:
                return METRIC;
            case DESC_METRIC:
                return "-" + METRIC;
            default:
                throw new IllegalArgumentException();
        }
    }

    private Comparator<ProfilesRow> comparator() {
        switch (sort) {
            case ASC_DIM:
                return isStringAttribute() ? DIMENSION_NAME_STRING_COMPARATOR : DIMENSION_NAME_DOUBLE_COMPARATOR;
            case DESC_DIM:
                return (isStringAttribute() ? DIMENSION_NAME_STRING_COMPARATOR : DIMENSION_NAME_DOUBLE_COMPARATOR).reversed();
            case ASC_METRIC:
                return METRIC_COMPARATOR;
            case DESC_METRIC:
                return METRIC_COMPARATOR.reversed();
            default:
                throw new IllegalArgumentException();
        }
    }

    private boolean isStringAttribute() {
        return attribute.startsWith("ym:p:customStringAttribute");
    }

    private enum Sort {
        ASC_DIM, DESC_DIM, ASC_METRIC, DESC_METRIC
    }
}
