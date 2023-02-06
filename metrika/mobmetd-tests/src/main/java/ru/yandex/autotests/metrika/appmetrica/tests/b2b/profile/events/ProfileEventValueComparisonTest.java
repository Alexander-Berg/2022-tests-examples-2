package ru.yandex.autotests.metrika.appmetrica.tests.b2b.profile.events;

import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileEventParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileSessionsEventsParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileSessionsParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileSessionsParametersBase;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.utils.ProfileEventTypeFetcher;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSession;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSessionEvents;
import ru.yandex.metrika.mobmet.profiles.model.events.ProfileEvent;
import ru.yandex.metrika.segments.apps.bundles.AppEventSource;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.APPMETRICA_PROD;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.IGOOODS;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.MOS_RU;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.SAMPLE;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_METRO;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_MUSIC;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.ZEN_APP_IOS;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.utils.ProfileEventTypeFetcher.CLIENT;
import static ru.yandex.autotests.metrika.appmetrica.utils.ProfileEventTypeFetcher.CRASH;
import static ru.yandex.autotests.metrika.appmetrica.utils.ProfileEventTypeFetcher.DEEPLINK;
import static ru.yandex.autotests.metrika.appmetrica.utils.ProfileEventTypeFetcher.ECOM;
import static ru.yandex.autotests.metrika.appmetrica.utils.ProfileEventTypeFetcher.ERROR;
import static ru.yandex.autotests.metrika.appmetrica.utils.ProfileEventTypeFetcher.PROTOBUF_CRASH;
import static ru.yandex.autotests.metrika.appmetrica.utils.ProfileEventTypeFetcher.PROTOBUF_ERROR;
import static ru.yandex.autotests.metrika.appmetrica.utils.ProfileEventTypeFetcher.REVENUE;
import static ru.yandex.metrika.segments.apps.bundles.AppEventSource.IMPORT_API;
import static ru.yandex.metrika.segments.apps.bundles.AppEventSource.SDK;

@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.Profile.Events.VALUE)
@Title("Значения событий профилей (сравнение отчётов)")
@RunWith(Parameterized.class)
public class ProfileEventValueComparisonTest {

    private static final UserSteps testingSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps referenceSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();

    @Parameterized.Parameter
    public Application application;

    @Parameterized.Parameter(1)
    public String device;

    @Parameterized.Parameter(2)
    public String profile;

    @Parameterized.Parameter(3)
    public String date;

    @Parameterized.Parameter(4)
    public ProfileEventTypeFetcher eventType;

    @Parameterized.Parameter(5)
    public AppEventSource eventSource;

    @Parameterized.Parameter(6)
    public boolean includeBackground;

    @Parameterized.Parameters(name = "Type: {4}, App: {0}, Device: {1}, Profile: {2}, Date: {3}, EventSource: {5}")
    public static Collection<Object[]> createParameters() {
        // Набор параметров указывает на страницу карточки профиля, на которой можно найти событие такого-то типа со
        // значением.
        return ImmutableList.of(
                params(APPMETRICA_PROD, "7868511879865266461", "13016085231003618736", "2019-05-21", CRASH, SDK, false),
                params(YANDEX_METRO, "14457612060689176845", "0", "2019-10-10", CRASH, SDK, false),
                params(YANDEX_METRO, "1000004653675223864", "0", "2018-06-05", CLIENT, SDK, false),
                params(MOS_RU, "12245584349596695058", "15552870018654947788", "2021-12-22", CLIENT, IMPORT_API, true),
                params(YANDEX_METRO, "4395827326561111730", "0", "2018-06-05", DEEPLINK, SDK, false),
                params(YANDEX_METRO, "5898738856864946357", "0", "2019-09-01", ERROR, SDK, false),
                params(SAMPLE, "2561215268046024947", "0", "2019-09-17", PROTOBUF_CRASH, SDK, false),
                params(ZEN_APP_IOS, "7290102501306725273", "0", "2019-09-11", PROTOBUF_ERROR, SDK, false),
                params(YANDEX_MUSIC, "2283496377093203124", "5367305657362534105", "2021-01-26", REVENUE, SDK, false),
                params(IGOOODS, "1410139133284918387", "14398371063764518150", "2021-01-26", ECOM, SDK, false)
        );
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(application);
    }

    @Test
    public void checkEventValuesMatch() {
        Event particularEvent = findEvent();

        ProfileSessionsParametersBase parameters = profilePageRequestParams(new ProfileEventParameters()
                .withSessionId(particularEvent.sessionId)
                .withEventNumber(particularEvent.properties.getEventBigNumber())
                .withEventSource(eventSource));

        String testingEventValue = eventType.getEventValueSupplier().apply(testingSteps, parameters);
        String referenceEventValue = eventType.getEventValueSupplier().apply(referenceSteps, parameters);
        assertThat("Значения событий совпадают", testingEventValue, equalTo(referenceEventValue));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    /**
     * Найдёт одно событие, обладающее значением, которое затем будем запрашивать, и имеющее тип, указанный в
     * параметрах теста.
     */
    private Event findEvent() {
        ProfileSessionsParametersBase sessionsRequestParams = profilePageRequestParams(new ProfileSessionsParameters()
                .withIncludeBackground(includeBackground)
                .withLimit(100));
        List<ProfileSession> sessions =
                testingSteps.onProfileSteps().getSessionsAll(sessionsRequestParams).getSessions();
        assumeThat("Список сессий не пуст", sessions, not(empty()));

        String sessionIds = sessions.stream().map(ProfileSession::getId).collect(Collectors.joining(","));
        ProfileSessionsParametersBase eventsRequestParams =
                profilePageRequestParams(new ProfileSessionsEventsParameters()
                        .withSessionIds(sessionIds)
                        .withLimit(100));
        List<ProfileSessionEvents> eventsPerSession =
                testingSteps.onProfileSteps().getSessionsEvents(eventsRequestParams);
        assumeThat("Список событий не пуст", eventsPerSession, not(empty()));

        Optional<Event> particularEvent = eventsPerSession.stream()
                .flatMap(session -> session.getEvents().stream()
                        .map(event -> new Event(session.getSessionId(), event)))
                .filter(event -> event.properties.getHasValue())
                .filter(event -> event.properties.getEventType() == eventType.appEventType)
                .filter(event -> event.properties.getEventSource() == eventSource)
                .findFirst();

        assumeThat("Событие тестируемого типа присутствует", particularEvent.isPresent(), is(true));
        return particularEvent.get();
    }

    private static class Event {
        final String sessionId;
        final ProfileEvent properties;

        Event(String sessionId, ProfileEvent properties) {
            this.sessionId = sessionId;
            this.properties = properties;
        }
    }

    private ProfileSessionsParametersBase profilePageRequestParams(ProfileSessionsParametersBase requestParams) {
        return requestParams
                .withDate1(date)
                .withDate2(date)
                .withAppId(application.get(Application.ID))
                .withDevice(device)
                .withProfileOrigin(profile);
    }

    private static Object[] params(Object... params) {
        return params;
    }
}
