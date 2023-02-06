package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.invariant;


import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.V2UserAcquisitionGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.DateDimension;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.UserAcquisitionParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.api.constructor.response.StaticRow;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.math.BigInteger;
import java.util.*;
import java.util.function.Function;

import static java.util.Comparator.*;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_METRO;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;

@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.TRAFFIC_SOURCES)
@Title("User Acquisition (инварианты сортировки)")
@RunWith(Parameterized.class)
public class UASortInvariantTest {

    private static final Application APPLICATION = YANDEX_METRO;

    private static final UserSteps user = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private TableReportParameters parameters;

    @Parameterized.Parameter
    public String dimensions;

    @Parameterized.Parameter(1)
    public String metrics;

    @Parameterized.Parameter(2)
    public String sort;

    @Parameterized.Parameter(3)
    public Comparator<StaticRow> expectedComparator;

    @Parameterized.Parameters(name = "Sort: {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param("campaign", "devices", "campaign", trackingIdComparator(0)))
                .add(param("campaign", "devices", "-campaign", trackingIdComparator(0).reversed()))
                .add(param("campaign", "event1Uniqs", "+event1Uniqs,campaign", metricComparator(0).thenComparing(trackingIdComparator(0))))
                .add(param("campaign", "event1Uniqs", "-event1Uniqs,campaign", metricComparator(0).reversed().thenComparing(trackingIdComparator(0))))
                .add(param("campaign", "event1Uniqs,conversion", "conversion,campaign",
                        nullLastComparator(metricExtractor(1)).thenComparing(trackingIdComparator(0))))
                .add(param("campaign", "event1Uniqs,conversion", "-conversion,campaign",
                        nullLastComparatorReversed(metricExtractor(1)).thenComparing(trackingIdComparator(0))))
                .build();
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(APPLICATION);
        parameters = new UserAcquisitionParameters()
                .withEvents(Collections.singletonList("application.start-session"))
                .withId(APPLICATION.get(ID))
                .withDate1(apiProperties().getUaStartDate())
                .withDate2(apiProperties().getUaEndDate())
                .withAccuracy("1")
                .withDimension(dimensions)
                .withMetric(metrics)
                .withSort(sort)
                .withDateDimension(DateDimension.DEFAULT.getValue());
    }

    @Test
    public void checkReportsMatch() {
        final V2UserAcquisitionGETSchema report = user.onTrafficSourceSteps().getReport(parameters);

        final List<StaticRow> actualRows = report.getData();
        assumeThat("Получен отчёт с достаточным количеством данных", actualRows, hasSize(greaterThan(5)));

        final List<StaticRow> expectedRows = new ArrayList<>(actualRows);
        expectedRows.sort(expectedComparator);

        assertThat("Порядок сортировки совпадает с ожидаемым", actualRows, equivalentTo(expectedRows));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    private static Comparator<StaticRow> trackingIdComparator(int campaignDimensionIndex) {
        // в базе id трекера сортируются как unsigned long
        return comparing((StaticRow row) -> new BigInteger(row.getDimensions().get(campaignDimensionIndex).get("id")));
    }

    private static Comparator<StaticRow> metricComparator(int metricIndex) {
        return comparing((StaticRow row) -> metricExtractor(metricIndex).apply(row));
    }

    private static Comparator<StaticRow> nullLastComparator(Function<StaticRow, Double> keyExtractor) {
        return comparing(keyExtractor, nullsLast(naturalOrder()));
    }

    private static Comparator<StaticRow> nullLastComparatorReversed(Function<StaticRow, Double> keyExtractor) {
        return comparing(keyExtractor, nullsLast(reverseOrder()));
    }

    private static Function<StaticRow, Double> metricExtractor(int metricIndex) {
        return (StaticRow row) -> row.getMetrics().get(metricIndex);
    }

    private static Object[] param(String dimensions, String metrics, String sort, Comparator<StaticRow> comparator) {
        return toArray(dimensions, metrics, sort, comparator);
    }
}
