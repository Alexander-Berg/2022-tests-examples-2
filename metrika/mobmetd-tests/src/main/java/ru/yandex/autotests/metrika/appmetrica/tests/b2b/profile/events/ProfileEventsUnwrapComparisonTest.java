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
import ru.yandex.metrika.mobmet.profiles.model.ProfileSession;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSessionEvents;
import ru.yandex.metrika.mobmet.profiles.model.events.ProfileEvent;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.APPMETRICA_PROD;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.MOS_RU;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_METRO;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;

@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.Profile.Events.UNWRAP)
@Title("Разворачивание подряд идущих событий (сравнение отчётов)")
@RunWith(Parameterized.class)
public class ProfileEventsUnwrapComparisonTest {

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

    @Parameterized.Parameters(name = "App: {0}, Device: {1}, Profile: {2}, Date: {3}")
    public static Collection<Object[]> createParameters() {
        // Набор параметров указывает на страницу карточки профиля,
        // на которой можно найти событие со свёрнутой цепочкой в плюсик.
        return ImmutableList.of(
                params(APPMETRICA_PROD, "4568510002758293985", "11761059686777282411", "2018-06-05"),
                params(YANDEX_METRO, "4855902302955251924", "0", "2018-06-05"),
                params(MOS_RU, "17663983670993537183", "5452148292918832679", "2021-12-22")
        );
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(application);
    }

    @Test
    public void checkUnwrappedEventsMatch() {
        Event particularEvent = findEvent();

        ProfileSessionsParametersBase parameters = profilePageRequestParams(new ProfileEventParameters()
                .withSessionId(particularEvent.sessionId)
                .withEventSource(particularEvent.properties.getEventSource())
                .withEventNumber(particularEvent.properties.getEventBigNumber())
                .withEventDateTime(particularEvent.properties.getDatetime()));

        List<ProfileEvent> testingEvents = testingSteps.onProfileSteps().getUnwrappedEvents(parameters);
        List<ProfileEvent> referenceEvents = referenceSteps.onProfileSteps().getUnwrappedEvents(parameters);

        assumeThat("Список развёрнутых событий не пуст", testingEvents, not(empty()));
        assertThat("Списки развёрнутых событий совпадают", testingEvents, equivalentTo(referenceEvents));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    /**
     * Найдёт событие, после которого идёт цепочка свёрнутых в плюсик событий
     */
    private Event findEvent() {
        ProfileSessionsParametersBase sessionsRequestParams = profilePageRequestParams(new ProfileSessionsParameters()
                .withIncludeBackground(true)
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
                .filter(event -> event.properties.getCollapsedEventsCount() > 0)
                .findFirst();

        assumeThat("Событие со свёрнутой цепочкой присутствует", particularEvent.isPresent(), is(true));
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
