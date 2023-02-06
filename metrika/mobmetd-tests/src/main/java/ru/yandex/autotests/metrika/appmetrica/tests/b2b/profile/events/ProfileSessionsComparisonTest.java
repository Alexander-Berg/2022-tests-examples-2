package ru.yandex.autotests.metrika.appmetrica.tests.b2b.profile.events;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Iterables;
import org.hamcrest.core.StringEndsWith;
import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileSessionsEventsParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileSessionsParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileSessionsParametersBase;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSession;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSessionEvents;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSessionsList;
import ru.yandex.metrika.mobmet.profiles.model.events.ProfileEvent;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.core.IsAnything.anything;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.DRIVE;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.IGOOODS;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.MOS_RU;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_METRO;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_MUSIC;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnSessions;

@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.Profile.Events.SESSIONS)
@Title("Сессии и события профилей (сравнение отчётов)")
@RunWith(Parameterized.class)
public final class ProfileSessionsComparisonTest {

    private static final UserSteps testingSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps referenceSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();

    @Parameterized.Parameter
    public long appId;

    @Parameterized.Parameter(1)
    public AppEventType eventType;

    @Parameterized.Parameter(2)
    public String device;

    @Parameterized.Parameter(3)
    public String profile;

    @Parameterized.Parameter(4)
    public String date;

    @Parameterized.Parameter(5)
    public boolean includeBackground;

    @Parameterized.Parameter(6)
    public int eventsLimit;

    @Rule
    public ParametersIgnoreRule ignoreRule = new ParametersIgnoreRule();

    private ProfileSessionsList testingSessions;

    private ProfileSessionsList referenceSessions;

    /**
     * Данные для тестов можно искать таким запросом:
     * SELECT DeviceIDHash
     * FROM mobile.generic_events_layer
     * WHERE (APIKey = 2) AND (EventDate = '2020-03-20') AND (EventType = 2) AND (SessionType = 0)
     * LIMIT 10
     */
    @Parameterized.Parameters(name = "AppId: {0}, Device: {1}, Profile: {2}, Date: {3}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                params(DRIVE, null, "5079417826719070756", "11990375219987788796", "2020-03-20", false, 100),
                params(YANDEX_METRO, null, "17127213825747888911", "0", "2020-03-20", false, 100),
                // session with ecom
                params(IGOOODS, null, "1410139133284918387", "14398371063764518150", "2021-01-26", false, 100),
                // session with revenue
                params(YANDEX_MUSIC, null, "2283496377093203124", "5367305657362534105", "2021-01-26", false,
                        100),
                // session with post-api
                params(MOS_RU, null, "17332383978430916549", "13560023847484018484", "2021-12-20", false, 100),
                // with background sessions only
                // select UUIDHash, DeviceIDHash, SessionID from mobile.events_all
                // where EventDate='2021-01-26' AND APIKey=2 AND SessionType=1
                // group by UUIDHash, DeviceIDHash, SessionID having count()>5 limit 10
                params(YANDEX_METRO, null, "905953840662883229", "0", "2021-01-26", true, 100),
                // единственная сессия в заданный день заходит на следующий день:
                // https://st.yandex-team.ru/MOBMET-14642#60a3b92ef52ce47527b88186
                params(IGOOODS, null, "5515566653415828919", "11183794435188687052", "2021-05-01", false,
                        1000),
                // поиск сессий с deeplinks
                params(YANDEX_METRO, AppEventType.EVENT_OPEN, "11315966326254053025", "0", "2022-01-26", false,
                        100)
        );
    }

    @IgnoreParameters.Tag(name = "known_issues")
    public static Collection<Object[]> ignoredParamsAsKnownIssues() {
        return ImmutableList.of(
        );
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(appId);
        ProfileSessionsParameters sessionsParameters =
                new ProfileSessionsParameters().withIncludeBackground(includeBackground);
        if (eventType != null) {
            sessionsParameters.withEventType(eventType);
        }
        ProfileSessionsParametersBase allSessionsParameters = withCommonParams(
                sessionsParameters);
        testingSessions = testingSteps.onProfileSteps().getSessions(allSessionsParameters);
        referenceSessions = referenceSteps.onProfileSteps().getSessions(allSessionsParameters);
    }

    @Test
    @IgnoreParameters(reason = "Известные проблемы", tag = "known_issues")
    public void checkSessionsMatch() {
        // Сравниваем id сессий для данного приложения, пользователя и дня
        assumeOnSessions(testingSessions, referenceSessions);

        assertThat("Множества сессий профиля за конкретные даты совпадают",
                testingSessions, equivalentTo(referenceSessions));
    }

    @Test
    @IgnoreParameters(reason = "Известные проблемы", tag = "known_issues")
    public void checkSessionEventsMatch() {
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
                .withLimit(eventsLimit);

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
                .withDate1(date)
                .withDate2(date)
                .withAppId(appId)
                .withDevice(device)
                .withProfileOrigin(profile);
    }

    private static Object[] params(Application app, AppEventType eventType, String device, String profile,
                                   String date, boolean includeBackground, int limit) {
        return new Object[]{app.get(Application.ID), eventType, device, profile, date, includeBackground, limit};
    }
}
