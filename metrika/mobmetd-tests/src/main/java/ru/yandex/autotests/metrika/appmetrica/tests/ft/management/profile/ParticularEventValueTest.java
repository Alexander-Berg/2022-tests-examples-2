package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.profile;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import com.google.common.io.Resources;
import com.google.gson.JsonParser;
import org.apache.commons.io.Charsets;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileEventParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.profile.events.ProfileSessionsParametersBase;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.utils.ProfileEventTypeFetcher;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.EAPTEKA;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.IGOOODS;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;

/**
 * Наверное этот тест должен был бы быть замокан или написан как аркадийный с данными в ClickHouse,
 * но сейчас так быстрее, проще и надёжнее
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.Profile.Events.VALUE)
@Title("Значения событий профилей (сравнение с образцом)")
@RunWith(Parameterized.class)
public class ParticularEventValueTest {

    private static final UserSteps testingSteps = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    @Parameterized.Parameter
    public Application application;

    @Parameterized.Parameter(1)
    public String device;

    @Parameterized.Parameter(2)
    public String profile;

    @Parameterized.Parameter(3)
    public String sessionId;

    @Parameterized.Parameter(4)
    public String uuid;

    @Parameterized.Parameter(5)
    public String eventNumber;

    @Parameterized.Parameter(6)
    public String date;

    @Parameterized.Parameter(7)
    public ProfileEventTypeFetcher eventType;

    @Parameterized.Parameter(8)
    public String expectedValuePath;

    private String expectedValue;

    @Parameterized.Parameters(name = "Type: {7}, Expected: {8}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                params(IGOOODS, "303811069521611459", "3863152342692081141", "10000001157", "15269137653945192194", 7,
                        "2021-01-26", ProfileEventTypeFetcher.ECOM, "ecom/show_screen.json"),
                params(IGOOODS, "1410139133284918387", "14398371063764518150", "10000000025", "7886044235667719966", 11,
                        "2021-01-26", ProfileEventTypeFetcher.ECOM, "ecom/show_product_card.json"),
                params(IGOOODS, "7680185077965277314", "18221171813911534990", "10000000135", "18252828143600935824",
                        1261,
                        "2021-01-26", ProfileEventTypeFetcher.ECOM, "ecom/show_product_details.json"),
                params(IGOOODS, "9775984382551012761", "10538350216728175761", "10000001127", "8545030984496006480",
                        147,
                        "2021-01-26", ProfileEventTypeFetcher.ECOM, "ecom/add_cart_item.json"),
                params(IGOOODS, "1410139133284918387", "14398371063764518150", "10000000025", "7886044235667719966", 21,
                        "2021-01-26", ProfileEventTypeFetcher.ECOM, "ecom/remove_cart_item.json"),
                params(IGOOODS, "280252459660241269", "10812964222798317579", "10000001144", "7113970298552302881", 44,
                        "2021-01-26", ProfileEventTypeFetcher.ECOM, "ecom/begin_checkout.json"),
                params(IGOOODS, "303811069521611459", "3863152342692081141", "10000001157", "15269137653945192194",
                        1125,
                        "2021-01-26", ProfileEventTypeFetcher.ECOM, "ecom/purchase.json"),
                params(EAPTEKA, "631752036039514536", "0", "10000000063", "195841229850832989", 89,
                        "2021-01-26", ProfileEventTypeFetcher.REVENUE, "revenue/with_payload.json")
        );
    }

    @SuppressWarnings("UnstableApiUsage")
    @Before
    public void setup() throws Exception {
        setCurrentLayerByApp(application);
        expectedValue = Resources.toString(ParticularEventValueTest.class.getResource(expectedValuePath),
                Charsets.UTF_8);
    }

    @Test
    public void checkEventValuesMatch() {

        ProfileSessionsParametersBase parameters = new ProfileEventParameters()
                .withSessionId(uuid + "." + device + "." + sessionId)
                .withEventNumber(eventNumber)
                .withDate1(date)
                .withDate2(date)
                .withAppId(application.get(Application.ID))
                .withDevice(device)
                .withProfileOrigin(profile);

        String testingEventValue = eventType.getEventValueSupplier().apply(testingSteps, parameters);

        JsonParser parser = new JsonParser();
        assertThat("Значение события равно ожидаемому", parser.parse(testingEventValue),
                equalTo(parser.parse(expectedValue)));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    public static Object[] params(Application app,
                                  String device,
                                  String profile,
                                  String sessionId,
                                  String uuid,
                                  int eventNumber,
                                  String date,
                                  ProfileEventTypeFetcher fetcher,
                                  String expectedResourcePath) {
        return new Object[]{app, device, profile, sessionId, uuid, String.valueOf(eventNumber), date, fetcher,
                expectedResourcePath};
    }
}
