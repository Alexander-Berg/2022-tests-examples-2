package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTracker;

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.ADD
})
@Title("Создание трекера с флагом проверки активности приложения")
public class AddTrackerActiveAppTest {

    private static final long APP_ID = Applications.PUSH_SAMPLE.get(ID);

    private final UserSteps manager = UserSteps.onTesting(SUPER_LIMITED);

    private CampaignWrapper campaignWrapper;

    private AppTargetUrl targetUrl;

    private String trackingId;

    @Before
    public void setup() {
        setCurrentLayerByApp(APP_ID);
        targetUrl = manager.onTrackerSteps().getOrCreateTargetUrl(APP_ID, defaultTargetUrl());
        campaignWrapper = new CampaignWrapper(defaultTracker());
        campaignWrapper.getCampaign().getPlatforms().get(0).withTargetUrlId(targetUrl.getId());
    }

    @Test
    public void testAddTracker() {
        trackingId = manager.onTrackerSteps().createTracker(APP_ID, campaignWrapper, true).getTrackingId();
    }

    @After
    public void teardown() {
        resetCurrentLayer();
        manager.onTrackerSteps().removeTrackerAndIgnoreResult(APP_ID, trackingId);
        manager.onTrackerSteps().deleteTargetUrlAndIgnoreResult(APP_ID, targetUrl.getId());
    }
}
