package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.credentials;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;
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

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Collection;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
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
@Title("Валидация ios сертификата при запуске пуш кампании")
@RunWith(Parameterized.class)
public class LaunchWithAppleCredentialsTest {

    private static final String YESTERDAY =
            DateTimeFormatter.ISO_LOCAL_DATE_TIME.format(LocalDateTime.now().plusDays(1));

    private static final UserSteps user = UserSteps.onTesting(Users.SUPER_LIMITED);

    @Parameter
    public PushCampaignWrapper pushCampaign;

    private Long appId;

    private long addedCampaignId;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                // Немедленная отправка
                .add(param(campaignWithSingleMessage(I_OS)
                        .withSendTimePolicy(NOW)
                        .withTimeZoneType(APPLICATION)))
                .add(param(campaignWithSingleMessage(I_OS)
                        .withSendTimePolicy(NOW)
                        .withTimeZoneType(DEVICE)))
                // Отложенная кампания
                .add(param(campaignWithSingleMessage(I_OS)
                        .withSendTimePolicy(DELAYED)
                        .withTimeZoneType(APPLICATION)
                        .withSendTime(YESTERDAY)))
                .add(param(campaignWithSingleMessage(I_OS)
                        .withSendTimePolicy(DELAYED)
                        .withTimeZoneType(DEVICE)
                        .withSendTime(YESTERDAY)))
                .build();

    }

    private static Object[] param(PushCampaignAdapter pushCampaign) {
        return toArray(wrap(pushCampaign));
    }

    @Before
    public void setup() {
        Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        user.onPushCredentialsSteps().updateAppleCredentials(appId, getAppleProdCredentials());

        PushCampaignAdapter addedCampaign = user.onPushCampaignSteps().addCampaign(
                wrap(pushCampaign.getCampaign().withAppId(appId)));
        addedCampaignId = addedCampaign.getId();
    }

    @Test
    public void checkNoErrors() {
        LaunchStatusAdapter actualStatus = user.onPushCampaignSteps().launchCampaign(addedCampaignId);
        assertThat("запуск кампании не содержит ошибку валидации сертификата", actualStatus,
                not(having(on(LaunchStatusAdapter.class).getErrors(),
                        hasItem(having(
                                on(ValidationErrorAdapter.class).getMessage(),
                                startsWith(PushValidationMessage.INVALID_CERT.message()))))));
    }

    @After
    public void tearDown() {
        user.onPushCampaignSteps().deleteCampaignIgnoringStatus(addedCampaignId);
        user.onPushCredentialsSteps().deleteAppleCredentialsIgnoringResult(appId, "production");
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
