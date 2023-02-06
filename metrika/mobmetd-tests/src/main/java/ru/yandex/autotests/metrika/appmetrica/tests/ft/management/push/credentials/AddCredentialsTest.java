package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.credentials;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

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

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.emptySummary;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getAppleProdCredentials;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getDevAppleCredentialsForDev;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getValidAndroidCredentials;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getValidHuaweiCredentials;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getValidWinCredentials;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.mask;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;


/**
 * Добавление учетных данных для рассылки сообщений
 *
 * @author dancingelf
 */
@Features(Requirements.Feature.Management.PUSH_CREDENTIALS)
@Stories({
        Requirements.Story.PushCredentials.ADD,
        Requirements.Story.PushCredentials.LIST
})
@Title("Добавление записей для рассылки пушей")
@RunWith(Parameterized.class)
public class AddCredentialsTest {

    private final UserSteps userSteps = UserSteps.onTesting(Users.SIMPLE_USER);

    private Long appId;

    @Parameterized.Parameter()
    public AndroidUpdateParameters androidCredentialsParams;

    @Parameterized.Parameter(1)
    public AppleCredentialsInfo prodApplePushCredentialsInfo;

    @Parameterized.Parameter(2)
    public AppleCredentialsInfo devApplePushCredentialsInfo;

    @Parameterized.Parameter(3)
    public HuaweiUpdateParameters huaweiCredentialsParams;

    @Parameterized.Parameter(4)
    public WinUpdateParameters winCredentialsParams;

    @Parameterized.Parameter(5)
    public PushCredentialsSummary expectedAndroidSummary;

    @Parameterized.Parameter(6)
    public PushCredentialsSummary expectedProdAppleSummary;

    @Parameterized.Parameter(7)
    public PushCredentialsSummary expectedDevAppleSummary;

    @Parameterized.Parameter(8)
    public PushCredentialsSummary expectedHuaweiSummary;

    @Parameterized.Parameter(9)
    public PushCredentialsSummary expectedWinSummary;

    @Parameterized.Parameter(10)
    public PushCredentialsSummary expectedAllSummary;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(params(
                        getValidAndroidCredentials(),
                        getAppleProdCredentials(),
                        getDevAppleCredentialsForDev(),
                        getValidHuaweiCredentials(),
                        getValidWinCredentials()))
                .build();
    }

    @Before
    public void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void addAndroidCredentials() {
        PushCredentialsSummary summary = userSteps.onPushCredentialsSteps().updateAndroidCredentials(appId,
                androidCredentialsParams);
        assertThat("данные учетной записи FCM корректно сохранены", summary, equivalentTo(expectedAndroidSummary));
    }

    @Test
    public void prodAddAppleCredentials() {
        PushCredentialsSummary summary = userSteps.onPushCredentialsSteps()
                .updateAppleCredentials(appId, prodApplePushCredentialsInfo);
        assertThat("данные учетной записи Apple корректно сохранены", summary, equivalentTo(expectedProdAppleSummary));
    }

    @Test
    public void devAddAppleCredentials() {
        PushCredentialsSummary summary = userSteps.onPushCredentialsSteps()
                .updateAppleCredentials(appId, devApplePushCredentialsInfo);
        assertThat("данные учетной записи Apple корректно сохранены", summary, equivalentTo(expectedDevAppleSummary));
    }

    @Test
    public void addHuaweiCredentials() {
        PushCredentialsSummary summary = userSteps.onPushCredentialsSteps()
                .updateHuaweiCredentials(appId, huaweiCredentialsParams);
        assertThat("данные учетной записи Huawei корректно сохранены", summary, equivalentTo(expectedHuaweiSummary));
    }

    @Test
    public void addWinCredentials() {
        PushCredentialsSummary summary = userSteps.onPushCredentialsSteps()
                .updateWinCredentials(appId, winCredentialsParams);
        assertThat("данные учетной записи Winphone сохранены", summary, equivalentTo(expectedWinSummary));
    }

    @Test
    public void listCredentials() {
        userSteps.onPushCredentialsSteps().updateAndroidCredentials(appId, androidCredentialsParams);
        userSteps.onPushCredentialsSteps().updateAppleCredentials(appId, prodApplePushCredentialsInfo);
        userSteps.onPushCredentialsSteps().updateHuaweiCredentials(appId, huaweiCredentialsParams);
        userSteps.onPushCredentialsSteps().updateWinCredentials(appId, winCredentialsParams);
        PushCredentialsSummary summary = userSteps.onPushCredentialsSteps().getCredentialsSummary(appId);

        assertThat("данные учетных записей корректно получены", summary, equivalentTo(expectedAllSummary));
    }

    @After
    public void teardown() {
        userSteps.onPushCredentialsSteps().deleteAndroidCredentialsIgnoringResult(appId);
        userSteps.onPushCredentialsSteps().deleteWinCredentialsIgnoringResult(appId);
        userSteps.onPushCredentialsSteps().deleteHuaweiCredentialsIgnoringResult(appId);
        userSteps.onPushCredentialsSteps()
                .deleteAppleCredentialsIgnoringResult(appId, prodApplePushCredentialsInfo.getCertType());
        userSteps.onPushCredentialsSteps()
                .deleteAppleCredentialsIgnoringResult(appId, devApplePushCredentialsInfo.getCertType());
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static Object[] params(AndroidUpdateParameters androidCredentials,
                                   AppleCredentialsInfo prodAppleCredentials,
                                   AppleCredentialsInfo devAppleCredentials,
                                   HuaweiUpdateParameters huaweiCredentials,
                                   WinUpdateParameters winCredentials) {

        PushCredentialsSummary expectedAndroidSummary = emptySummary()
                .withAndroidCredentialsAreValid(true)
                .withAndroidAuthKeyMasked(mask(androidCredentials.getAuthKey()));

        PushCredentialsSummary expectedProdAppleSummary = emptySummary()
                .withAppleProdCredentialsAreValid(true);

        PushCredentialsSummary expectedDevAppleSummary = emptySummary()
                .withAppleDevCredentialsAreValid(true);

        PushCredentialsSummary expectedWinSummary = emptySummary()
                .withWinCredentialsAreValid(true)
                .withWinPackageSecurityIdentifierMasked(mask(winCredentials.getPackageSecurityIdentifier()))
                .withWinSecretKeyMasked(mask(winCredentials.getSecretKey()));

        PushCredentialsSummary expectedHuaweiSummary = emptySummary()
                .withHuaweiCredentialsAreValid(true)
                .withHuaweiClientId(huaweiCredentials.getClientId())
                .withHuaweiClientSecretMasked(mask(huaweiCredentials.getClientSecret()));

        PushCredentialsSummary expectedAllSummary = emptySummary()
                .withAndroidCredentialsAreValid(true)
                .withAndroidAuthKeyMasked(mask(androidCredentials.getAuthKey()))
                .withAppleProdCredentialsAreValid(true)
                .withHuaweiCredentialsAreValid(true)
                .withHuaweiClientId(huaweiCredentials.getClientId())
                .withHuaweiClientSecretMasked(mask(huaweiCredentials.getClientSecret()))
                .withWinCredentialsAreValid(true)
                .withWinPackageSecurityIdentifierMasked(mask(winCredentials.getPackageSecurityIdentifier()))
                .withWinSecretKeyMasked(mask(winCredentials.getSecretKey()));

        return toArray(androidCredentials, prodAppleCredentials, devAppleCredentials, huaweiCredentials, winCredentials,
                expectedAndroidSummary, expectedProdAppleSummary, expectedDevAppleSummary, expectedHuaweiSummary,
                expectedWinSummary, expectedAllSummary);
    }
}
