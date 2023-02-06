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
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.FORBIDDEN;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTracker;

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.ADD
})
@Title("Создание трекера с флагом проверки активности приложения (негативный)")
public class AddTrackerActiveAppNegativeTest {
    /**
     * Берём приложение, у которого никогда не было событий и, скорее всего, не будет.
     * Создавать пустое приложение не годится, поскольку тестовые management-данные
     * отстают от прода. Отсюда следует, что новое заведённое приложение может получить id реального
     * приложения с прода, для которого проверка активности выдала бы true.
     */
    private static final long APP_ID = Applications.YANDEX_SEARCH_FOR_WP_TESTING.get(ID);

    private final UserSteps manager = UserSteps.onTesting(SUPER_LIMITED);

    private AppTargetUrl targetUrl;

    @Before
    public void setup() {
        setCurrentLayerByApp(APP_ID);
        targetUrl = manager.onTrackerSteps().getOrCreateTargetUrl(APP_ID, defaultTargetUrl());
    }

    @Test
    public void testAddTrackerFails() {
        CampaignWrapper campaignWrapper = new CampaignWrapper(defaultTracker());
        campaignWrapper.getCampaign().getPlatforms().get(0).withTargetUrlId(targetUrl.getId());
        manager.onTrackerSteps().createTrackerAndExpectError(APP_ID, campaignWrapper, true, FORBIDDEN);
    }

    @After
    public void teardown() {
        resetCurrentLayer();
        manager.onTrackerSteps().deleteTargetUrlAndIgnoreResult(APP_ID, targetUrl.getId());
    }
}
