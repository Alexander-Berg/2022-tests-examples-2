package ru.yandex.autotests.metrika.appmetrica.tests.b2b.profile.events;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileSessionsParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileSessionsParametersBase;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.profiles.model.ProfileEventNamesList;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.APPMETRICA_PROD;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.MOS_RU;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_METRO;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;

@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.Profile.Events.NAMES)
@Title("Поиск по именам событий профилей (сравнение отчётов)")
@RunWith(Parameterized.class)
public class ProfileEventNamesComparisonTest {

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
    public String eventNameFilter;

    @Parameterized.Parameter(5)
    public int expectedResponseSize;

    @Parameterized.Parameters(name = "Filter: {4}, AppId: {0}, Device: {1}, Profile: {2}, Date: {3}")
    public static Collection<Object[]> createParameters() {
        // Набор параметров указывает на сессию, в которой имеются события с именами (пока что только client events).
        // Последние два параметра - это фильтр для поиска по именам и ожидаемая длина ответа.
        return ImmutableList.of(
                params(APPMETRICA_PROD, "4568510002758293985", "11761059686777282411", "2018-05-07", null, 7),
                params(APPMETRICA_PROD, "4568510002758293985", "11761059686777282411", "2018-05-07", "dashboard", 2),
                params(APPMETRICA_PROD, "4568510002758293985", "11761059686777282411", "2018-05-07", "", 7),
                params(APPMETRICA_PROD, "4568510002758293985", "11761059686777282411", "2018-05-07", "abacaba", 0),
                params(YANDEX_METRO, "1000004653675223864", "0", "2018-06-05", null, 10),
                params(YANDEX_METRO, "1000004653675223864", "0", "2018-06-05", "session", 2),
                params(MOS_RU, "1384176037553908", "8118986606180983203", "2021-12-22", null, 3),
                params(MOS_RU, "1384176037553908", "8118986606180983203", "2021-12-22", "Дети в школе", 2)
        );
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(application);
    }

    @Test
    public void checkEventNamesMatch() {
        ProfileSessionsParametersBase parameters = new ProfileSessionsParameters()
                .withEventName(eventNameFilter)
                .withDate1(date)
                .withDate2(date)
                .withAppId(application.get(Application.ID))
                .withDevice(device)
                .withProfileOrigin(profile);

        ProfileEventNamesList testingEventNames = testingSteps.onProfileSteps().getClientEventNames(parameters);
        ProfileEventNamesList referenceEventNames = referenceSteps.onProfileSteps().getClientEventNames(parameters);

        assumeThat("Список имён событий имеет ожидаемую длину", testingEventNames.getNames(),
                hasSize(expectedResponseSize));
        assertThat("Списки имён событий совпадают", testingEventNames, equalTo(referenceEventNames));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    private static Object[] params(Object... params) {
        return params;
    }
}
