package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.crash;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.errors.ManagementError;
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
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.ECOMMERCE;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_PROTOBUF_CRASH;

@Features(Requirements.Feature.Management.CRASH)
@Stories({
        Requirements.Story.Crash.ALERT_SETTINGS
})
@Title("Управление настройками оповещений о крешах (негативный)")
@RunWith(Parameterized.class)
public class CrashAlertSettingsNegativeTest {

    private final UserSteps userSteps = UserSteps.onTesting(Users.SIMPLE_USER);

    private long appId;

    @Parameterized.Parameter
    public ManagementError error;

    @Parameterized.Parameter(1)
    public CrashAlertSettingsSummary illegalSettingsSummary;

    @Parameterized.Parameters(name = "Error: {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                params(CRASH_ALERT_SETTINGS_ILLEGAL_EMAIL,
                        defaultCrashAlertSettingsSummary("illegal_email")),
                params(CRASH_ALERT_SETTINGS_RATE_MUST_LESS_1,
                        defaultCrashVelocityAlertSettingsSummary(asList(
                                velocityAlertConfig(EVENT_PROTOBUF_CRASH, VelocityAlertType.TOTAL, 0)))),
                params(CRASH_ALERT_SETTINGS_RATE_MUST_GREATER_100_000_000,
                        defaultCrashVelocityAlertSettingsSummary(asList(
                                velocityAlertConfig(EVENT_PROTOBUF_CRASH, VelocityAlertType.TOTAL, 100_000_001)))),
                params(CRASH_ALERT_SETTINGS_ILLEGAL_EVENT_TYPE,
                        defaultCrashVelocityAlertSettingsSummary(asList(
                                velocityAlertConfig(ECOMMERCE, VelocityAlertType.TOTAL, 1_000_000)))),
                params(CRASH_ALERT_SETTINGS_ILLEGAL_EVENT_TYPE,
                        defaultCrashOpenAlertSettingsSummary(asList(ECOMMERCE)))
        );
    }

    private static Object[] params(ManagementError error, CrashAlertSettingsSummary settingsSummary) {
        return new Object[]{error, settingsSummary};
    }

    @Before
    public void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void testUpdate() {
        userSteps.onCrashAlertSettingsSteps().updateAndExpectError(appId, illegalSettingsSummary, error);
    }


    @After
    public void teardown() {
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
