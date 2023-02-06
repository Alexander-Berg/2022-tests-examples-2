package ru.yandex.autotests.metrika.appmetrica.tests.b2b.profile.events;

import com.google.common.collect.Iterables;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileSessionsEventsParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileSessionsParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileSessionsParametersBase;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSession;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSessionEvents;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSessionsList;
import ru.yandex.metrika.mobmet.profiles.model.events.ProfileEvent;
import ru.yandex.metrika.segments.apps.bundles.AppEventSource;

import java.util.List;
import java.util.stream.Collectors;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.MOS_RU;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnSessions;

public final class ProfileSessionsAllComparisonTest {

    private static final UserSteps testingSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps referenceSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withBaseUrl(apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private ProfileSessionsList testingSessions;

    private ProfileSessionsList referenceSessions;

    @Before
    public void setup() {
        setCurrentLayerByApp(MOS_RU.get(ID));
        ProfileSessionsParametersBase sessionsParameters = withCommonParams(
                new ProfileSessionsParameters().withIncludeBackground(true));

        testingSessions = testingSteps.onProfileSteps().getSessionsAll(sessionsParameters);
        referenceSessions = referenceSteps.onProfileSteps().getSessionsAll(sessionsParameters);
    }

    @Test
    public void checkSessionsMatch() {
        // Сравниваем id сессий для данного приложения, пользователя и дня
        assumeOnSessions(testingSessions, referenceSessions);

        assertThat("Множества сессий профиля за конкретные даты совпадают",
                testingSessions, equivalentTo(referenceSessions));
    }

    @Test
    public void checkSdkSessionEventsMatch() {
        // Сравниваем id сессий для данного приложения, пользователя и дня
        assumeOnSessions(testingSessions, referenceSessions);

        assumeThat("Множества сессий профиля за конкретные даты совпадают",
                testingSessions, equivalentTo(referenceSessions));

        List<String> sessionIds = testingSessions.getSessions().stream()
                .map(ProfileSession::getId)
                .collect(Collectors.toList());

        // Сравниваем события для первой сессии из списка сессий
        ProfileSessionsParametersBase firstSessionParameters = withCommonParams(new ProfileSessionsEventsParameters()
                .withSessionIds(Iterables.getFirst(sessionIds, "0")))
                .withLimit(10);

        List<ProfileSessionEvents> testingData =
                testingSteps.onProfileSteps().getSessionsEvents(firstSessionParameters);
        List<ProfileSessionEvents> referenceData =
                referenceSteps.onProfileSteps().getSessionsEvents(firstSessionParameters);
        assumeThat("Множества сессий в ответе непустое", testingData, not(empty()));
        assumeThat("Множества сессий в ответе непустое", referenceData, not(empty()));

        List<ProfileEvent> testingEvents = testingData.stream().findFirst().get().getEvents();
        List<ProfileEvent> referenceEvents = testingData.stream().findFirst().get().getEvents();
        assumeThat("Множества событий в сессии непустое", testingEvents, not(empty()));
        assumeThat("Множества событий в сессии непустое", referenceEvents, not(empty()));

        assertThat("Cессии совпадают", testingData, equivalentTo(referenceData));
    }

    @Test
    public void checkPostApiSessionEventsMatch() {
        // Сравниваем id сессий для данного приложения, пользователя и дня
        assumeOnSessions(testingSessions, referenceSessions);

        assumeThat("Множества сессий профиля за конкретные даты совпадают",
                testingSessions, equivalentTo(referenceSessions));

        List<ProfileSession> sessions = testingSessions.getSessions();

        // Сравниваем события для первого блока с post-api событиями из списка сессий
        String firstPostApiBlockId = sessions.stream()
                .filter(s -> s.getEventSource() == AppEventSource.IMPORT_API)
                .findFirst()
                .orElseThrow(() -> new IllegalStateException("post-api block not found"))
                .getId();
        ProfileSessionsParametersBase firstSessionParameters = withCommonParams(new ProfileSessionsEventsParameters()
                .withSessionIds(firstPostApiBlockId))
                .withLimit(10);

        List<ProfileSessionEvents> testingData =
                testingSteps.onProfileSteps().getSessionsEvents(firstSessionParameters);
        List<ProfileSessionEvents> referenceData =
                referenceSteps.onProfileSteps().getSessionsEvents(firstSessionParameters);
        assumeThat("Множества сессий в ответе непустое", testingData, not(empty()));
        assumeThat("Множества сессий в ответе непустое", referenceData, not(empty()));

        List<ProfileEvent> testingEvents = testingData.stream().findFirst().get().getEvents();
        List<ProfileEvent> referenceEvents = testingData.stream().findFirst().get().getEvents();
        assumeThat("Множества событий в сессии непустое", testingEvents, not(empty()));
        assumeThat("Множества событий в сессии непустое", referenceEvents, not(empty()));

        assertThat("Cессии совпадают", testingData, equivalentTo(referenceData));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    private ProfileSessionsParametersBase withCommonParams(ProfileSessionsParametersBase params) {
        return params
                .withDate1("2021-12-20")
                .withDate2("2021-12-20")
                .withAppId(MOS_RU.get(ID))
                .withDevice("17332383978430916549")
                .withProfileOrigin("13560023847484018484");
    }
}
