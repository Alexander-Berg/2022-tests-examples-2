package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.nullifier;

import com.google.common.collect.ImmutableList;
import org.hamcrest.Matcher;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.V2UserAcquisitionGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.TSSource;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.UserAcquisitionParameters;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.api.constructor.response.StaticRow;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Collections.singletonList;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnResponse;

@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.TRAFFIC_SOURCES)
@Title("Источники трафика v2 (зануление метрик при выборе несовместимых фильтров)")
@RunWith(Parameterized.class)
public class UANullifierTest {

    private static final UserSteps testingSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final Long APP_ID = Applications.ANDROID_APP.get(Application.ID);

    @Parameterized.Parameter
    public Matcher<Double> nullMatcher;

    @Parameterized.Parameter(1)
    public String dimension;

    @Parameterized.Parameter(2)
    public String metrics;

    @Parameterized.Parameter(3)
    public String filter;

    @Parameterized.Parameters(name = "dimensions={1}, metrics={2}, filter={3}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                new Object[]{nullValue(), "campaign", "clicks", "age == 25"},
                new Object[]{nullValue(), "campaign", "conversion", "age == 25"},
                new Object[]{nullValue(), "campaign", "conversion", "regionCountry==225 AND age == 25"},
                new Object[]{nullValue(), "campaign", "conversion", "regionCountry==225 OR age == 25"},
                new Object[]{nullValue(), "campaign", "clicks", "gender == 'Female'"},
                new Object[]{nullValue(), "campaign", "clicks", "isMan == 'no'"},
                new Object[]{nullValue(), "campaign", "clicks", "isWoman == 'yes'"},
                new Object[]{nullValue(), "campaign", "clicks", "ageInterval == '25'"},
                new Object[]{nullValue(), "campaign", "clicks", "exists ym:ce:age with (ym:ce:regionCountry == 225)"},
                new Object[]{nullValue(), "gender", "clicks", ""},
                new Object[]{nullValue(), "ageInterval", "clicks", ""},
                new Object[]{nullValue(), "campaign", "clicks", "ageInterval == '25'"},
                new Object[]{notNullValue(), "campaign", "clicks", "regionCountry==225"},
                new Object[]{notNullValue(), "campaign", "clicks", "exists ym:ce:user with (ym:ce:age == 25)"},
                new Object[]{notNullValue(), "campaign", "clicks", "exists ym:ts:user with (ym:ts:age == 25)"},
                new Object[]{nullValue(), "installSourceType", "deeplinks", ""},
                new Object[]{notNullValue(), "installSourceType", "devices", ""}
        );
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(APP_ID);
    }

    @Test
    public void checkNullifiedClicks() {
        TableReportParameters parameters = new UserAcquisitionParameters()
                .withEvents(singletonList("hotel visit"))
                .withSource(TSSource.INSTALLATION)
                .withId(APP_ID)
                .withDate1(AppMetricaApiProperties.apiProperties().getUaStartDate())
                .withDate2(AppMetricaApiProperties.apiProperties().getUaEndDate())
                .withMetric(metrics)
                .withDimension(dimension)
                .withFilters(filter)
                .withAccuracy("0.05");

        V2UserAcquisitionGETSchema report = testingSteps.onTrafficSourceSteps().getReport(parameters);

        assumeOnResponse(report);

        assertThat("Клики [не] занулились",
                report.getData().stream().map(StaticRow::getMetrics).collect(toList()),
                everyItem(everyItem(nullMatcher)));

        assertThat("Клики в totals [не] занулились",
                report.getTotals(),
                everyItem(nullMatcher));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }
}
