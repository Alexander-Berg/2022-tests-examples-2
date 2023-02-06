package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import java.util.List;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.CoreMatchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.INFO
})
@Title("Проверка создания целевой ссылки")
public class AddTargetUrlTest {

    private static final UserSteps owner = UserSteps.onTesting(SIMPLE_USER_2);
    private Long appId;
    private String campaignTrackingId;
    private Long targetUrlId;

    @Before
    public void setup() {
        Application addedApplication = owner.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void addUnusedTargetUrl() {
        AppTargetUrl expected = defaultTargetUrl();
        AppTargetUrl createdTargetUrl = owner.onTrackerSteps().createTargetUrl(appId, expected);
        expected.withId(targetUrlId).withDeletable(true);

        targetUrlId = createdTargetUrl.getId();

        List<AppTargetUrl> targetUrls = owner.onTrackerSteps().getTargetUrls(appId);
        assertThat("список ЦС содержит целевую ссылку, эквивалентную ожидаемой", targetUrls,
                hasItem(equivalentTo(expected)));
    }

    @Test
    public void addUsedTargetUrl() {
        AppTargetUrl expected = defaultTargetUrl();
        AppTargetUrl createdTargetUrl = owner.onTrackerSteps().createTargetUrl(appId, expected);
        expected.withId(targetUrlId).withDeletable(false);

        targetUrlId = createdTargetUrl.getId();

        CampaignWrapper campaignWrapper = new CampaignWrapper(defaultTracker());
        campaignWrapper.getCampaign().getPlatforms().get(0).withTargetUrlId(targetUrlId);
        campaignTrackingId = owner.onTrackerSteps().createTracker(appId, campaignWrapper).getTrackingId();

        List<AppTargetUrl> targetUrls = owner.onTrackerSteps().getTargetUrls(appId);
        assertThat("список ЦС содержит целевую ссылку, эквивалентную ожидаемой", targetUrls,
                hasItem(equivalentTo(expected)));
    }

    @After
    public void teardown() {
        owner.onTrackerSteps().removeTrackerAndIgnoreResult(appId, campaignTrackingId);
        owner.onTrackerSteps().deleteTargetUrlAndIgnoreResult(appId, targetUrlId);
        owner.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
