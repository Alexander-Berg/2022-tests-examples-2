package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.invariant;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
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

import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_METRO;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;

/**
 * Created by graev on 11/05/2017.
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.TRAFFIC_SOURCES)
@Title("User Acquisition (инварианты)")
@RunWith(Parameterized.class)
public final class UAInvariantTest {

    private static final UserSteps user = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private TableReportParameters parameters;

    @Parameterized.Parameter
    public Application application;

    @Parameterized.Parameter(1)
    public String dimensions;

    @Parameterized.Parameter(2)
    public String metrics;

    @Parameterized.Parameters(name = "Application: {0}; Dimensions: {1}; Metrics: {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(YANDEX_METRO, "campaign", "devices"))
                .add(param(YANDEX_METRO, "publisher", "loyalUsers"))
                .add(param(YANDEX_METRO, "urlParamKey", "sessions"))
                .build();
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(application);
        parameters = new UserAcquisitionParameters()
                .withEvents(Collections.emptyList())
                .withId(application.get(ID))
                .withDate1(apiProperties().getUaStartDate())
                .withDate2(apiProperties().getUaEndDate())
                .withAccuracy("1")
                .withDimension(dimensions)
                .withMetric("conversion," + metrics)
                .withDateDimension(DateDimension.DEFAULT.getValue());
    }

    @Test
    public void checkReportsMatch() {
        final List<Double> conversions = user.onTrafficSourceSteps().getReport(parameters)
                .getData()
                .stream()
                .map(StaticRow::getMetrics)
                .map(m -> m.get(0))
                .collect(Collectors.toList());

        assertThat("все значения конверсии не превосходят 100%", conversions,
                everyItem(anyOf(nullValue(), lessThanOrEqualTo(100.0))));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    private static Object[] param(Application application, String dimensions, String metrics) {
        return toArray(application, dimensions, metrics);
    }
}
