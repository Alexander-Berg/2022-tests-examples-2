package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.credentials;

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

import java.util.Collection;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.*;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;


/**
 * Удаление учетных данных для рассылки сообщений
 *
 * @author dancingelf
 */
@Features(Requirements.Feature.Management.PUSH_CREDENTIALS)
@Stories({
        Requirements.Story.PushCredentials.ADD,
        Requirements.Story.PushCredentials.DELETE
})
@Title("Удаление учетных записей рассылки пушей")
@RunWith(Parameterized.class)
public class DeleteCredentialsTest {

    private final UserSteps userSteps = UserSteps.onTesting(Users.SIMPLE_USER);

    private Long appId;

    @Parameterized.Parameter()
    public AndroidUpdateParameters androidCredentialsParams;

    @Parameterized.Parameter(value = 1)
    public AppleCredentialsInfo applePushCredentialsInfo;

    @Parameterized.Parameter(value = 2)
    public WinUpdateParameters winCredentialsParams;

    @Parameterized.Parameter(value = 3)
    public HuaweiUpdateParameters huaweiCredentialsParams;

    @Parameterized.Parameter(value = 4)
    public PushCredentialsSummary expectedEmptySummary;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(toArray(
                        getValidAndroidCredentials(),
                        getAppleProdCredentials(),
                        getValidWinCredentials(),
                        getValidHuaweiCredentials(),
                        emptySummary()))
                .build();
    }

    @Before
    public void setup() {
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void deleteAndroidCredentials() {
        userSteps.onPushCredentialsSteps().updateAndroidCredentials(appId, androidCredentialsParams);
        PushCredentialsSummary summary = userSteps.onPushCredentialsSteps().deleteAndroidCredentials(appId);
        assertThat("данные FCM удалены", summary, equivalentTo(expectedEmptySummary));
    }

    @Test
    public void deleteAppleCredentials() {
        userSteps.onPushCredentialsSteps().updateAppleCredentials(appId, applePushCredentialsInfo);
        PushCredentialsSummary summary =
                userSteps.onPushCredentialsSteps().deleteAppleCredentials(appId, applePushCredentialsInfo.getCertType());
        assertThat("данные учетной записи Apple удалены", summary, equivalentTo(expectedEmptySummary));
    }

    @Test
    public void deleteWinCredentials() {
        userSteps.onPushCredentialsSteps().updateWinCredentials(appId, winCredentialsParams);
        PushCredentialsSummary summary = userSteps.onPushCredentialsSteps().deleteWinCredentials(appId);
        assertThat("данные учетной записи Winphone удалены", summary, equivalentTo(expectedEmptySummary));
    }

    @Test
    public void deleteHuaweiCredentials() {
        userSteps.onPushCredentialsSteps().updateHuaweiCredentials(appId, huaweiCredentialsParams);
        PushCredentialsSummary summary =
                userSteps.onPushCredentialsSteps().deleteHuaweiCredentials(appId);
        assertThat("данные учетной записи Huawei удалены", summary, equivalentTo(expectedEmptySummary));
    }

    @After
    public void teardown() {
        userSteps.onPushCredentialsSteps().deleteAndroidCredentialsIgnoringResult(appId);
        userSteps.onPushCredentialsSteps().deleteAppleCredentialsIgnoringResult(appId, applePushCredentialsInfo.getCertType());
        userSteps.onPushCredentialsSteps().deleteWinCredentialsIgnoringResult(appId);
        userSteps.onPushCredentialsSteps().deleteHuaweiCredentialsIgnoringResult(appId);
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
