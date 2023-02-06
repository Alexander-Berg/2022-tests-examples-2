package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker.postback.omni;

import org.junit.After;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.RedirectsCampaignAppIdPostbackPartnerIdCheckPUTSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Partner;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.Postback;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.ZORKA;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.randomOmniPostback;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.trackerWithRandomOmniPostback;

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.ADD
})
@Title("Предупреждение о дублировании омни-постбека")
public class OmniPostbackConflictTest {

    private static final long APP_ID = Applications.PUSH_SAMPLE.get(ID);

    private static final long PARTNER_ID = ZORKA.get(Partner.ID);

    private final UserSteps manager = UserSteps.onTesting(SUPER_LIMITED);

    private Long targetUrlId;

    private String trackingId;

    @Test
    @Title("Проверка наличия конфликта с омни-постбеком")
    public void checkOmniPostbackConflictPresence() {
        targetUrlId = manager.onTrackerSteps().getOrCreateTargetUrl(APP_ID, defaultTargetUrl()).getId();
        CampaignWrapper campaignWrapper = new CampaignWrapper(trackerWithRandomOmniPostback(PARTNER_ID));
        campaignWrapper.getCampaign().getPlatforms().get(0).withTargetUrlId(targetUrlId);

        Campaign createdTracker = manager.onTrackerSteps().createTracker(APP_ID, campaignWrapper, true);
        assumeThat("У созданного трекера есть постбек", createdTracker.getPostbacks(), not(empty()));
        trackingId = createdTracker.getTrackingId();

        Postback createdPostback = createdTracker.getPostbacks().get(0);
        Postback newPostback = createdPostback.withId(0L);

        RedirectsCampaignAppIdPostbackPartnerIdCheckPUTSchema checkStatus =
                manager.onTrackerSteps().checkPostback(APP_ID, PARTNER_ID, newPostback);

        assertThat("Статус проверки нового постбека совпадает с ожидаемым", checkStatus.getCheck(), equalTo("false"));
        assertThat("Сообщение проверки постбека содержит указание на трекер с конлфиктом",
                checkStatus.getCheckMessage(), containsString(createdTracker.getTrackingId()));
    }

    @Test
    @Title("Проверка отсутствия конфликта с омни-постбеком")
    public void checkOmniPostbackConflictAbsence() {
        RedirectsCampaignAppIdPostbackPartnerIdCheckPUTSchema checkStatus =
                manager.onTrackerSteps().checkPostback(APP_ID, PARTNER_ID, randomOmniPostback());

        assertThat("Статус проверки нового постбека совпадает с ожидаемым", checkStatus.getCheck(), equalTo("true"));
        assertThat("Сообщение проверки постбека пустое", checkStatus.getCheckMessage(), nullValue());
    }

    @Test
    @Title("Проверка отсутствия стандартной валидации постбека")
    public void checkNoDefaultValidation() {
        Postback emptyPostback = new Postback();
        RedirectsCampaignAppIdPostbackPartnerIdCheckPUTSchema checkStatus =
                manager.onTrackerSteps().checkPostback(APP_ID, PARTNER_ID, emptyPostback);

        assertThat("Статус проверки нового постбека совпадает с ожидаемым", checkStatus.getCheck(), equalTo("true"));
        assertThat("Сообщение проверки постбека пустое", checkStatus.getCheckMessage(), nullValue());
    }

    @After
    public void teardown() {
        manager.onTrackerSteps().removeTrackerAndIgnoreResult(APP_ID, trackingId);
        manager.onTrackerSteps().deleteTargetUrlAndIgnoreResult(APP_ID, targetUrlId);
    }
}
