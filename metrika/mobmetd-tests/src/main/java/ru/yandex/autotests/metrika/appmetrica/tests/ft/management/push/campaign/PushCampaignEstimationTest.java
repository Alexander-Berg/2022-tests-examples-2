package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.CampaignEstimationAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.model.CampaignEstimationInnerLocaleUniqs;
import ru.yandex.metrika.mobmet.push.common.campaigns.model.CampaignEstimationInnerPlatformUniqs;
import ru.yandex.metrika.mobmet.push.response.EstimationResponse;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.concurrent.TimeUnit;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.util.Arrays.asList;
import static org.awaitility.Awaitility.given;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;
import static org.junit.Assert.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.PushCampaigns.SENT_PUSH_CAMPAIGN_ID;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials.PushCampaignParameter.FORCE;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.minimalCampaign;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.PushCampaignWrapper.wrap;
import static ru.yandex.metrika.mobmet.push.service.EstimatingSituation.LAUNCHED;
import static ru.yandex.metrika.mobmet.push.service.EstimatingSituation.READY;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.ANDROID;
import static ru.yandex.metrika.segments.apps.misc.PushPlatform.I_OS;

@Features(Requirements.Feature.Management.PUSH_CAMPAIGN)
@Stories({
        Requirements.Story.PushCampaign.ESTIMATION
})
@Title("Оценка аудитории пуш кампании")
public class PushCampaignEstimationTest {
    private static final UserSteps user = UserSteps.onTesting(Users.SUPER_LIMITED);

    private static final EstimationResponse expectedSentPushCampaignEstimation = new EstimationResponse()
            .withStatus(READY)
            .withEstimation(new CampaignEstimationAdapter()
                    .withTotalUniqs(38L)
                    .withPlatformUniqs(asList(
                            new CampaignEstimationInnerPlatformUniqs().withPlatform(ANDROID).withUniqs(22L),
                            new CampaignEstimationInnerPlatformUniqs().withPlatform(I_OS).withUniqs(16L)
                    ))
                    .withLocaleUniqs(asList(
                            new CampaignEstimationInnerLocaleUniqs()
                                    .withLocale("ru")
                                    .withLocaleName("русский")
                                    .withUniqs(30L),
                            new CampaignEstimationInnerLocaleUniqs()
                                    .withLocale("en")
                                    .withLocaleName("английский")
                                    .withUniqs(8L)
                    )));

    private Long addedCampaignId;

    @Before
    public void setUp() {
        PushCampaignAdapter addedCampaign = user.onPushCampaignSteps().addCampaign(wrap(minimalCampaign()));
        addedCampaignId = addedCampaign.getId();
    }

    @After
    public void tearDown() {
        if (addedCampaignId != null) {
            user.onPushCampaignSteps().deleteCampaignIgnoringStatus(addedCampaignId);
        }
    }

    @Test
    public void checkEstimationResponse() {
        EstimationResponse estimationResponse = user.onPushCampaignSteps().estimate(addedCampaignId, FORCE);
        assumeThat("На force-запрос оценки аудитории пуш кампании возвращается ответ со статусом launched",
                LAUNCHED, equalTo(estimationResponse.getStatus()));

        EstimationResponse readyEstimationResponse = waitUntilEstimationComplete(addedCampaignId);
        assertThat("Число уникальных устройств больше либо равно 0",
                readyEstimationResponse.getEstimation().getTotalUniqs(), greaterThan(0L));
        assertThat("Статус завершенной оценки равен ready", READY, equalTo(readyEstimationResponse.getStatus()));
    }

    @Test
    public void checkSentAudience() {
        EstimationResponse estimationResponse = user.onPushCampaignSteps().estimate(SENT_PUSH_CAMPAIGN_ID);
        assertThat("Аудитория отправленной пуш кампании равна ожидаемой",
                estimationResponse, equivalentTo(expectedSentPushCampaignEstimation));
    }

    private EstimationResponse waitUntilEstimationComplete(Long pushCampaignId) {
        return given().ignoreExceptions()
                .await()
                .atMost(60, TimeUnit.SECONDS)
                .until(
                        () -> user.onPushCampaignSteps().estimate(pushCampaignId),
                        having(
                                on(EstimationResponse.class).getStatus(),
                                equalTo(READY)
                        )
                );

    }
}
