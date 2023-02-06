package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.crash;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.crash.alerts.VelocityAlertType;
import ru.yandex.metrika.mobmet.crash.model.CrashAlertSettingsSummary;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_PROTOBUF_CRASH;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_PROTOBUF_ERROR;

@Features(Requirements.Feature.Management.CRASH)
@Stories({
        Requirements.Story.Crash.ALERT_SETTINGS
})
@Title("Изменение настроек оповещений о крешах")
@RunWith(Parameterized.class)
public class CrashAlertSettingsUpdateTest {

    private final UserSteps userSteps = UserSteps.onTesting(Users.SIMPLE_USER);

    private long appId;

    @Parameter
    public String caseDescription;

    @Parameter(1)
    public CrashAlertSettingsSummary expectedSettingsSummary;

    @Parameters(name = "Settings: {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                params("Только email", defaultCrashAlertSettingsSummary()),
                params("Email и оповещения о новых группах крещей",
                        defaultCrashOpenAlertSettingsSummary(asList(EVENT_PROTOBUF_CRASH))),
                params("Email и оповещения о новых группах крещей и ошибок",
                        defaultCrashOpenAlertSettingsSummary(asList(EVENT_PROTOBUF_CRASH, EVENT_PROTOBUF_ERROR))),
                params("Email и оповещения о долях сессий с крешами", defaultCrashVelocityAlertSettingsSummary(asList(
                        velocityAlertConfig(EVENT_PROTOBUF_CRASH, VelocityAlertType.TOTAL, 1000)))),
                params("Email и оповещения о нескольких типах долей сессий с крешами",
                        defaultCrashVelocityAlertSettingsSummary(asList(
                                velocityAlertConfig(EVENT_PROTOBUF_CRASH, VelocityAlertType.TOTAL, 1000),
                                velocityAlertConfig(EVENT_PROTOBUF_ERROR, VelocityAlertType.TOTAL, 1000),
                                velocityAlertConfig(EVENT_PROTOBUF_CRASH, VelocityAlertType.PARTICULAR_GROUP, 100),
                                velocityAlertConfig(EVENT_PROTOBUF_ERROR, VelocityAlertType.PARTICULAR_GROUP, 100)))),
                params("Все настройки оповещений", defaultFullAlertSettingsSummary())
        );
    }

    private static Object[] params(String caseDescription, CrashAlertSettingsSummary settingsSummary) {
        return new Object[]{caseDescription, settingsSummary};
    }

    @Before
    public void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void testUpdate() {
        userSteps.onCrashAlertSettingsSteps().update(appId, expectedSettingsSummary);
        CrashAlertSettingsSummary actualSettingsSummary = userSteps.onCrashAlertSettingsSteps().get(appId);
        assertThat("настройки оповещений о крешах эквивалентны ожидаемым", actualSettingsSummary,
                equivalentTo(expectedSettingsSummary));
    }


    @After
    public void teardown() {
        userSteps.onCrashAlertSettingsSteps().clearSettings(appId);
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
