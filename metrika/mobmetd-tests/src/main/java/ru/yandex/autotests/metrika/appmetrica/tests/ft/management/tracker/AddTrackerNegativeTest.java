package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.segments.apps.misc.MobPlatform;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.DOUBLECLICK_EMPTY_CAT;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.INVALID_DOUBLECLICK_FINGERPRINT_WINDOW;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.INVALID_DOUBLECLICK_PLATFORM;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.INVALID_STRICT_ATTR_WINDOW;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.REMARKETING_TRACKER_MISSING_DEEPLINK;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.REMARKETING_TRACKER_MULTIPLE_PLATFORM;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPlatform;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTrackerWithThreeMonthsAttrWindow;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.doubleClickTrackerWithEmptyCat;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.doubleClickTrackerWithFingerprintWindow;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.doubleClickTrackerWithPlatform;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.remarketingMyTargetTracker;


@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.ADD,
        Requirements.Story.Tracker.INFO,
        Requirements.Story.Tracker.LIST
})
@Title("Создание трекера (негативный)")
public final class AddTrackerNegativeTest {

    private final UserSteps owner = UserSteps.onTesting(SIMPLE_USER);

    private AppTargetUrl targetUrl;

    private Long appId;

    @Before
    public void setup() {
        Application addedApplication = owner.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        targetUrl = owner.onTrackerSteps().getOrCreateTargetUrl(appId, defaultTargetUrl());
    }

    @Test
    public void testNotAdwordsTrackerWithThreeMonthsAttributionWindow() {
        CampaignWrapper campaign = new CampaignWrapper(defaultTrackerWithThreeMonthsAttrWindow());
        campaign.getCampaign().getPlatforms().get(0).setTargetUrlId(targetUrl.getId());
        owner.onTrackerSteps().createTrackerAndExpectError(appId, campaign, INVALID_STRICT_ATTR_WINDOW);
    }

    @Test
    public void testDoubleClickFailsOnTrackerWithPlatform() {
        CampaignWrapper campaign = new CampaignWrapper(doubleClickTrackerWithPlatform());
        owner.onTrackerSteps().createTrackerAndExpectError(appId, campaign, INVALID_DOUBLECLICK_PLATFORM);
    }

    @Test
    public void testDoubleClickFailsOnNotEmptyFingerprintWindow() {
        CampaignWrapper campaign = new CampaignWrapper(doubleClickTrackerWithFingerprintWindow());
        owner.onTrackerSteps().createTrackerAndExpectError(appId, campaign, INVALID_DOUBLECLICK_FINGERPRINT_WINDOW);
    }

    @Test
    public void testRemarketingFailsOnEmptyDeeplink() {
        CampaignWrapper campaign = new CampaignWrapper(remarketingMyTargetTracker());
        owner.onTrackerSteps().createTrackerAndExpectError(appId, campaign, REMARKETING_TRACKER_MISSING_DEEPLINK);
    }

    @Test
    public void testRemarketingFailsOnMultiplePlatforms() {
        CampaignWrapper campaign = new CampaignWrapper(remarketingMyTargetTracker()
                .withPlatforms((asList(
                        defaultPlatform(MobPlatform.ANDROID),
                        defaultPlatform(MobPlatform.I_OS)))));
        owner.onTrackerSteps().createTrackerAndExpectError(appId, campaign, REMARKETING_TRACKER_MULTIPLE_PLATFORM);
    }

    /**
     * Other required fields are checked in UT TrackerPreprocessorTest
     */
    @Test
    public void testDoubleClickFailsOnNotEmptyCat() {
        CampaignWrapper campaign = new CampaignWrapper(doubleClickTrackerWithEmptyCat());
        owner.onTrackerSteps().createTrackerAndExpectError(appId, campaign, DOUBLECLICK_EMPTY_CAT);
    }

    @After
    public void teardown() {
        owner.onTrackerSteps().deleteTargetUrlAndIgnoreResult(appId, targetUrl.getId());
        owner.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
