package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.segments.apps.misc.MobPlatform;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.INFO
})
@Title("Проверка удаления диплинков и ЦС (позитивный)")
public class DeleteAppTrackingUrlsTest {
    private static final UserSteps owner = UserSteps.onTesting(SIMPLE_USER);
    private Long appId;
    private Long targetUrlId;
    private Long deepLinkId;

    @Before
    public void setup() {
        Application addedApplication = owner.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
        targetUrlId = owner.onTrackerSteps().createTargetUrl(appId, defaultTargetUrl()).getId();
        deepLinkId = owner.onTrackerSteps().createDeepLink(appId, defaultDeepLink(MobPlatform.ANDROID)).getId();
    }

    @Test
    public void deleteUnusedTargetUrl() {
        owner.onTrackerSteps().deleteTargetUrlAndExpectSuccess(appId, targetUrlId);
    }

    @Test
    public void deleteUnusedDeepLink() {
        owner.onTrackerSteps().deleteDeepLinkAndExpectSuccess(appId, deepLinkId);
    }

    @After
    public void teardown() {
        owner.onTrackerSteps().deleteTargetUrlAndIgnoreResult(appId, targetUrlId);
        owner.onTrackerSteps().deleteDeepLinkAndIgnoreResult(appId, deepLinkId);
        owner.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}
