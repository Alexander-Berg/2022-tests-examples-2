package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.redirect.AppDeepLink;
import ru.yandex.metrika.segments.apps.misc.MobPlatform;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.CoreMatchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultDeepLink;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.INFO
})
@Title("Проверка создания диплинка")
public class AddDeeplinkTest {

    private static final UserSteps owner = UserSteps.onTesting(SIMPLE_USER);
    private Long appId;
    private String campaignTrackingId;
    private Long deepLinkId;
    private Long targetUrlId;

    @Before
    public void setup() {
        Application addedApplication = owner.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void addUnusedDeepLink() {
        AppDeepLink createdDeepLink = owner.onTrackerSteps().createDeepLink(appId, defaultDeepLink(MobPlatform.ANDROID));
        String deepLinkTitle = createdDeepLink.getTitle();
        deepLinkId = createdDeepLink.getId();
        targetUrlId = owner.onTrackerSteps().createTargetUrl(appId, defaultTargetUrl()).getId();

        List<AppDeepLink> deepLinks = owner.onTrackerSteps().getDeepLinks(appId);
        AppDeepLink expected = defaultDeepLink(MobPlatform.ANDROID).withDeletable(true).withId(deepLinkId).withTitle(deepLinkTitle);
        assertThat("список диплинков содержит диплинк, эквивалентный ожидаемому", deepLinks,
                hasItem(equivalentTo(expected)));
    }

    @Test
    public void addUsedDeepLink() {
        AppDeepLink createdDeepLink = owner.onTrackerSteps().createDeepLink(appId, defaultDeepLink(MobPlatform.ANDROID));
        String deepLinkTitle = createdDeepLink.getTitle();
        deepLinkId = createdDeepLink.getId();
        targetUrlId = owner.onTrackerSteps().createTargetUrl(appId, defaultTargetUrl()).getId();
        CampaignWrapper campaignWrapper = new CampaignWrapper(defaultTracker());
        campaignWrapper.getCampaign().getPlatforms().get(0).withDeepLinkId(deepLinkId);
        campaignWrapper.getCampaign().getPlatforms().get(0).withTargetUrlId(targetUrlId);
        campaignTrackingId = owner.onTrackerSteps().createTracker(appId, campaignWrapper).getTrackingId();

        List<AppDeepLink> deepLinks = owner.onTrackerSteps().getDeepLinks(appId);
        AppDeepLink expected = defaultDeepLink(MobPlatform.ANDROID).withDeletable(false).withId(deepLinkId).withTitle(deepLinkTitle);
        assertThat("список диплинков содержит диплинк, эквивалентный ожидаемому", deepLinks,
                hasItem(equivalentTo(expected)));
    }

    @After
    public void teardown() {
        owner.onTrackerSteps().removeTrackerAndIgnoreResult(appId, campaignTrackingId);
        owner.onTrackerSteps().deleteDeepLinkAndIgnoreResult(appId, deepLinkId);
        owner.onTrackerSteps().deleteTargetUrlAndIgnoreResult(appId, targetUrlId);
        owner.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
