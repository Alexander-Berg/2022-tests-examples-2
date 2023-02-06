package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.credentials;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.info.push.credentials.AppleCredentialsInfo;
import ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials.AndroidUpdateParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials.HuaweiUpdateParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials.WinUpdateParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.push.response.PushCredentialsSummary;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.ANDROID_INVALID_CREDENTIALS;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.APPLE_DEV_CREDENTIALS;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.APPLE_INVALID_CREDENTIALS;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.HUAWEI_INVALID_CREDENTIALS;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.WIN_INVALID_CREDENTIALS;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.emptySummary;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getBadPassAppleCredentials;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getDevAppleCredentialsForProd;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getExpiredAppleCredentials;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getInvalidAndroidCredentials;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getInvalidHuaweiCredentials;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getInvalidWinCredentials;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getRevokedAppleCredentials;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;


/**
 * Негативный тест добавления учетных данных для рассылки сообщений
 *
 * @author dancingelf
 */
@Features(Requirements.Feature.Management.PUSH_CREDENTIALS)
@Stories({
        Requirements.Story.PushCredentials.ADD,
        Requirements.Story.PushCredentials.LIST
})
@Title("Добавление записей для рассылки пушей (негативный)")
public class AddCredentialsNegativeTest {

    private final UserSteps userSteps = UserSteps.onTesting(Users.SIMPLE_USER);

    private Long appId;

    private static final AndroidUpdateParameters INVALID_ANDROID_CREDENTIALS_CERT = getInvalidAndroidCredentials();
    private static final AppleCredentialsInfo BAD_PASS_APPLE_CREDENTIALS_CERT = getBadPassAppleCredentials();
    private static final WinUpdateParameters INVALID_WIN_CREDENTIALS_CERT = getInvalidWinCredentials();
    private static final HuaweiUpdateParameters INVALID_HUAWEI_CREDENTIALS_CERT = getInvalidHuaweiCredentials();

    @Before
    public void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void addAndroidCredentials() {
        userSteps.onPushCredentialsSteps()
                .updateAndroidCredentialsAndExpectError(appId, INVALID_ANDROID_CREDENTIALS_CERT, ANDROID_INVALID_CREDENTIALS);
    }

    @Test
    public void addBadPassAppleCredentials() {
        userSteps.onPushCredentialsSteps()
                .updateAppleCredentialsAndExpectError(appId, BAD_PASS_APPLE_CREDENTIALS_CERT, APPLE_INVALID_CREDENTIALS);
    }

    @Test
    public void addAppleDevCredentialsForProdEnv() {
        userSteps.onPushCredentialsSteps()
                .updateAppleCredentialsAndExpectError(appId, getDevAppleCredentialsForProd(), APPLE_DEV_CREDENTIALS);
    }

    @Test
    public void addAppleRevokedCredentialsForProdEnv() {
        userSteps.onPushCredentialsSteps()
                .updateAppleCredentialsAndExpectError(appId, getRevokedAppleCredentials(), APPLE_INVALID_CREDENTIALS);
    }

    @Test
    public void addAppleExpiredCredentialsForProdEnv() {
        userSteps.onPushCredentialsSteps()
                .updateAppleCredentialsAndExpectError(appId, getExpiredAppleCredentials(), APPLE_INVALID_CREDENTIALS);
    }

    @Test
    public void addWinCredentials() {
        userSteps.onPushCredentialsSteps()
                .updateWinCredentialsAndExpectError(appId, INVALID_WIN_CREDENTIALS_CERT, WIN_INVALID_CREDENTIALS);
    }

    @Test
    public void addHuaweiCredentials() {
        userSteps.onPushCredentialsSteps()
                .updateHuaweiCredentialsAndExpectError(appId, INVALID_HUAWEI_CREDENTIALS_CERT, HUAWEI_INVALID_CREDENTIALS);
    }

    @Test
    public void listCredentials() {
        userSteps.onPushCredentialsSteps()
                .updateAndroidCredentialsAndExpectError(appId, INVALID_ANDROID_CREDENTIALS_CERT, ANDROID_INVALID_CREDENTIALS);
        userSteps.onPushCredentialsSteps()
                .updateAppleCredentialsAndExpectError(appId, BAD_PASS_APPLE_CREDENTIALS_CERT, APPLE_INVALID_CREDENTIALS);
        userSteps.onPushCredentialsSteps()
                .updateWinCredentialsAndExpectError(appId, INVALID_WIN_CREDENTIALS_CERT, WIN_INVALID_CREDENTIALS);
        userSteps.onPushCredentialsSteps()
                .updateHuaweiCredentialsAndExpectError(appId, INVALID_HUAWEI_CREDENTIALS_CERT, HUAWEI_INVALID_CREDENTIALS);
        PushCredentialsSummary summary = userSteps.onPushCredentialsSteps().getCredentialsSummary(appId);

        assertThat("данные учетных записей сохранены", summary, equivalentTo(emptySummary()));
    }

    @After
    public void teardown() {
        userSteps.onPushCredentialsSteps().deleteAndroidCredentialsIgnoringResult(appId);
        userSteps.onPushCredentialsSteps().deleteWinCredentialsIgnoringResult(appId);
        userSteps.onPushCredentialsSteps().deleteAppleCredentialsIgnoringResult(appId, "production");
        userSteps.onPushCredentialsSteps().deleteAppleCredentialsIgnoringResult(appId, "development");
        userSteps.onPushCredentialsSteps().deleteHuaweiCredentialsIgnoringResult(appId);
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
