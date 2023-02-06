package ru.yandex.autotests.metrika.appmetrica.tests.b2b;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.TSEventParameters;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.model.events.EventsResponse;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnEvents;

/**
 * Проверяем, что множество событий для отчета по источникам трафика не изменилось
 * <p>
 * Created by graev on 12/04/2017.
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.TRAFFIC_SOURCES)
@Title("Источники трафика (сравнение событий)")
public final class TSEventsComparisonTest {

    private static final UserSteps testingSteps = UserSteps.builder()
            .withBaseUrl(AppMetricaApiProperties.apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps referenceSteps = UserSteps.builder()
            .withBaseUrl(AppMetricaApiProperties.apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final Long APP_ID = Applications.PUSH_SAMPLE.get(Application.ID);

    private TSEventParameters parameters;

    @Before
    public void setup() {
        setCurrentLayerByApp(APP_ID);
        parameters = new TSEventParameters()
                .withAppId(APP_ID);
    }

    @Test
    public void checkReportsMatch() {
        final EventsResponse testingData = testingSteps.onTrafficSourceSteps().getEvents(parameters);
        final EventsResponse referenceData = referenceSteps.onTrafficSourceSteps().getEvents(parameters);

        assumeOnEvents(testingData, referenceData);

        assertThat("множества событий совпадают", testingData, equivalentTo(referenceData));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

}
