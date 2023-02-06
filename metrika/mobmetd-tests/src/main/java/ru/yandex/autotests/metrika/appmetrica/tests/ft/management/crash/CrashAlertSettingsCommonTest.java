package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.crash;

import org.hamcrest.core.IsEqual;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.crash.alerts.settings.EmailState;
import ru.yandex.metrika.mobmet.crash.model.CrashAlertSettingsSummary;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.concurrent.TimeUnit;

import static org.awaitility.Awaitility.given;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.CRASH_EMAIL_CONFIRMATION_TIMEOUT_NOT_EXPIRED;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultCrashAlertSettingsSummary;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.CRASH)
@Stories({
        Requirements.Story.Crash.ALERT_SETTINGS
})
@Title("Управление настройками оповещений о крешах")
public class CrashAlertSettingsCommonTest {

    private final UserSteps userSteps = UserSteps.onTesting(Users.SIMPLE_USER);

    private long appId;

    @Before
    public void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void testDeleteEmail() {
        CrashAlertSettingsSummary settingsSummary = defaultCrashAlertSettingsSummary();

        userSteps.onCrashAlertSettingsSteps().update(appId, settingsSummary);
        CrashAlertSettingsSummary actualSettingsSummary = userSteps.onCrashAlertSettingsSteps().get(appId);
        assumeThat("настройки оповещений о крешах эквивалентны ожидаемым", actualSettingsSummary,
                equivalentTo(settingsSummary));

        userSteps.onCrashAlertSettingsSteps().update(appId, defaultCrashAlertSettingsSummary(null));
        actualSettingsSummary = userSteps.onCrashAlertSettingsSteps().get(appId);
        assumeThat("Статус email absent", actualSettingsSummary.getCrashAlertSettings().getEmailState(),
                equalTo(EmailState.ABSENT));
        assertThat("email не задан", actualSettingsSummary.getCrashAlertSettings().getEmail(),
                nullValue());
    }

    @Test
    public void testRepeatEmailConfirmation() {
        CrashAlertSettingsSummary settingsSummary = defaultCrashAlertSettingsSummary();
        userSteps.onCrashAlertSettingsSteps().update(appId, settingsSummary);

        given().ignoreExceptions()
                .await()
                .atMost(90, TimeUnit.SECONDS)
                .pollDelay(1, TimeUnit.SECONDS)
                .pollInterval(5, TimeUnit.SECONDS)
                .until(
                        () -> userSteps.onCrashAlertSettingsSteps()
                                .repeatConfirmation(appId).getSuccess(),
                        IsEqual.equalTo(true));
    }

    @Test
    public void testRepeatEmailConfirmationBeforeTimeout() {
        CrashAlertSettingsSummary settingsSummary = defaultCrashAlertSettingsSummary();
        userSteps.onCrashAlertSettingsSteps().update(appId, settingsSummary);
        userSteps.onCrashAlertSettingsSteps().repeatConfirmationAndExpectError(appId,
                CRASH_EMAIL_CONFIRMATION_TIMEOUT_NOT_EXPIRED);
    }

    @After
    public void teardown() {
        userSteps.onCrashAlertSettingsSteps().clearSettings(appId);
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
