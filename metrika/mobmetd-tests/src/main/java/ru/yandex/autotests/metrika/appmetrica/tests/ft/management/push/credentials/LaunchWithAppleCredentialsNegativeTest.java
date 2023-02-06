package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.credentials;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.errors.PushValidationMessage;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PushCampaignWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.LaunchStatusAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.ValidationErrorAdapter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import javax.annotation.Nullable;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Collection;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.APP_WITH_EXPIRED_IOS_CERT;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.PushCredentialsCreator.getAppleProdCredentials;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.campaignWithSingleMessage;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.PushCampaignWrapper.wrap;
import static ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaignBriefInnerSendTimePolicy.DELAYED;
import static ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaignBriefInnerSendTimePolicy.NOW;
import static ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaignBriefInnerTimeZoneType.APPLICATION;
import static ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaignBriefInnerTimeZoneType.DEVICE;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.I_OS;

@Features(Requirements.Feature.Management.PUSH_CAMPAIGN)
@Stories({
        Requirements.Story.PushCampaign.ADD,
        Requirements.Story.PushCampaign.LAUNCH
})
@Title("Валидация ios сертификата при запуске пуш кампании (негативный)")
@RunWith(Parameterized.class)
public class LaunchWithAppleCredentialsNegativeTest {

    private static final String DATE_WITH_EXPIRED_CERT =
            DateTimeFormatter.ISO_LOCAL_DATE_TIME.format(LocalDateTime.now().plusYears(20));

    private static final UserSteps user = UserSteps.onTesting(Users.SUPER_LIMITED);

    /**
     * Если параметр null, то нужно создать приложение.
     * Этот хак нам нужен, так чтобы протестировать TimePolicy==NOW, ведь создать "налету" приложение
     * с истёкшим сертификатом нельзя. Может быть стоит для этой цели добавить специальную внутренюю ручку.
     */
    @Parameterized.Parameter(0)
    public Long appId;

    @Parameterized.Parameter(1)
    public PushCampaignWrapper pushCampaign;

    private boolean createdApp;

    private long addedCampaignId;

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(APP_WITH_EXPIRED_IOS_CERT.get(ID),
                        campaignWithSingleMessage(I_OS)
                        .withSendTimePolicy(NOW)
                        .withTimeZoneType(APPLICATION)))
                .add(param(APP_WITH_EXPIRED_IOS_CERT.get(ID),
                        campaignWithSingleMessage(I_OS)
                        .withSendTimePolicy(NOW)
                        .withTimeZoneType(DEVICE)))
                .add(param(APP_WITH_EXPIRED_IOS_CERT.get(ID),
                        campaignWithSingleMessage(I_OS)
                                .withSendTimePolicy(DELAYED)
                                .withTimeZoneType(DEVICE)
                                .withSendTime(DATE_WITH_EXPIRED_CERT)))
                .add(param(APP_WITH_EXPIRED_IOS_CERT.get(ID),
                        campaignWithSingleMessage(I_OS)
                                .withSendTimePolicy(DELAYED)
                                .withTimeZoneType(APPLICATION)
                                .withSendTime(DATE_WITH_EXPIRED_CERT)))
                .add(param(null,
                        campaignWithSingleMessage(I_OS)
                        .withSendTimePolicy(DELAYED)
                        .withTimeZoneType(DEVICE)
                        .withSendTime(DATE_WITH_EXPIRED_CERT)))
                .add(param(null,
                        campaignWithSingleMessage(I_OS)
                        .withSendTimePolicy(DELAYED)
                        .withTimeZoneType(APPLICATION)
                        .withSendTime(DATE_WITH_EXPIRED_CERT)))
                .build();
    }

    @Before
    public void setup() {
        if (appId == null) {
            createdApp = true;
            Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
            appId = addedApplication.getId();
            user.onPushCredentialsSteps().updateAppleCredentials(appId, getAppleProdCredentials());
        }

        PushCampaignAdapter addedCampaign = user.onPushCampaignSteps().addCampaign(
                wrap(pushCampaign.getCampaign().withAppId(appId)));
        addedCampaignId = addedCampaign.getId();
    }

    @Test
    public void checkErrorOnExpiredCert() {
        LaunchStatusAdapter actualStatus = user.onPushCampaignSteps().launchCampaign(addedCampaignId);
        assertThat("запуск кампании содержит ошибку валидации сертификата", actualStatus,
                having(on(LaunchStatusAdapter.class).getErrors(),
                        hasItem(having(
                                on(ValidationErrorAdapter.class).getMessage(),
                                startsWith(PushValidationMessage.INVALID_CERT.message())))));
    }

    @After
    public void tearDown() {
        user.onPushCampaignSteps().deleteCampaignIgnoringStatus(addedCampaignId);
        if (createdApp) {
            // удаляем приложение, только если сами его создали
            user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
            user.onPushCredentialsSteps().deleteAppleCredentialsIgnoringResult(appId, "production");
        }
    }

    private static Object[] param(@Nullable Long appId, PushCampaignAdapter pushCampaign) {
        return toArray(appId, wrap(pushCampaign));
    }
}
