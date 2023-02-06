package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.CampaignSource;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTracker;

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.ADD
})
@Title("Нельзя переопределить источник возникновения трекера")
@RunWith(Parameterized.class)
public class AddTrackerCheckSourceTest {

    @Parameterized.Parameter
    public CampaignSource campaignSource;

    private static final long APP_ID = Applications.PUSH_SAMPLE.get(ID);

    private final UserSteps manager = UserSteps.onTesting(SUPER_LIMITED);

    private CampaignWrapper campaignWrapper;

    private AppTargetUrl targetUrl;

    private String trackingId;

    @Parameterized.Parameters(name = "Input source: {0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(new Object[]{CampaignSource.APPMETRICA})
                .add(new Object[]{CampaignSource.DIRECT_UAC})
                .add(new Object[]{null})
                .build();
    }

    @Before
    public void setup() {
        targetUrl = manager.onTrackerSteps().getOrCreateTargetUrl(APP_ID, defaultTargetUrl());
        campaignWrapper = new CampaignWrapper(defaultTracker());
        campaignWrapper.getCampaign().getPlatforms().get(0).withTargetUrlId(targetUrl.getId());
    }

    @Test
    public void checkAddedCampaignSourceIsAppMetrica() {
        trackingId = manager.onTrackerSteps().createTracker(APP_ID, campaignWrapper, true).getTrackingId();
        Campaign campaign = manager.onTrackerSteps().getTracker(APP_ID, trackingId);
        assertThat("Источник добавленного трекера - это АппМетрика", campaign.getSource(), equalTo(CampaignSource.APPMETRICA));
    }

    @Test
    public void checkEditedCampaignSourceIsAppMetrica() {
        Campaign addedCampaign = manager.onTrackerSteps().createTracker(APP_ID, campaignWrapper, true);
        trackingId = addedCampaign.getTrackingId();
        manager.onTrackerSteps().editTracker(APP_ID, trackingId, new CampaignWrapper(addedCampaign.withSource(campaignSource)));

        Campaign actualCampaign = manager.onTrackerSteps().getTracker(APP_ID, trackingId);
        assertThat("Источник добавленного трекера - это АппМетрика", actualCampaign.getSource(), equalTo(CampaignSource.APPMETRICA));
    }

    @After
    public void teardown() {
        manager.onTrackerSteps().removeTrackerAndIgnoreResult(APP_ID, trackingId);
        manager.onTrackerSteps().deleteTargetUrlAndIgnoreResult(APP_ID, targetUrl.getId());
    }
}
