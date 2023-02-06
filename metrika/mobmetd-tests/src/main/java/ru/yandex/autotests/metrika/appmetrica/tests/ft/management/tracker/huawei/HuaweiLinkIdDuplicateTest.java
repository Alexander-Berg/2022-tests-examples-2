package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker.huawei;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.appmetrica.actions.EditAction;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.HUAWEI_LINK_ID_CONFLICT;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.changeHuaweiLinkId;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.huaweiAdsTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.randomHuaweiLinkId;

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.ADD
})
@Title("Проверка дублирования Huawei Link ID")
public class HuaweiLinkIdDuplicateTest {

    private static final long APP_ID = Applications.PUSH_SAMPLE.get(ID);

    private final UserSteps manager = UserSteps.onTesting(SUPER_LIMITED);

    private CampaignWrapper trackerToCreate;

    private String trackingId;
    private String otherTrackingId;

    @Before
    public void init() {
        trackerToCreate = new CampaignWrapper(huaweiAdsTracker(randomHuaweiLinkId()));

        Campaign createdTracker = manager.onTrackerSteps().createTracker(APP_ID, trackerToCreate);
        trackingId = createdTracker.getTrackingId();
    }

    @Test
    @Title("Проверка конфликта с уже используемым Huawei Link ID при создании трекера")
    public void checkTrackerCreation() {
        manager.onTrackerSteps().createTrackerAndExpectError(APP_ID, trackerToCreate, HUAWEI_LINK_ID_CONFLICT);
    }

    @Test
    @Title("Проверка конфликта с уже используемым Huawei Link ID при редактировании трекера")
    public void checkTrackerEdit() {
        String originalLinkId = trackerToCreate.getCampaign().getHuaweiLinkId();
        String newLinkId = randomHuaweiLinkId();
        assumeThat("Случайные Huawei Link ID не совпадают", originalLinkId, not(equalTo(newLinkId)));

        CampaignWrapper otherTrackerToCreate = new CampaignWrapper(huaweiAdsTracker(newLinkId));
        Campaign otherCreatedTracker = manager.onTrackerSteps().createTracker(APP_ID, otherTrackerToCreate);
        otherTrackingId = otherCreatedTracker.getTrackingId();

        EditAction<Campaign, Campaign> editAction = changeHuaweiLinkId(originalLinkId);
        CampaignWrapper updatedOtherTracker = new CampaignWrapper(editAction.getUpdate(otherCreatedTracker));

        manager.onTrackerSteps().editTrackerAndExpectError(APP_ID, otherTrackingId, updatedOtherTracker, HUAWEI_LINK_ID_CONFLICT);
    }

    @Test
    @Title("Проверка конфликта с уже используемым Huawei Link ID при восстановлении трекера")
    public void checkTrackerRestoration() {
        manager.onTrackerSteps().removeTracker(APP_ID, trackingId);

        Campaign otherCreatedTracker = manager.onTrackerSteps().createTracker(APP_ID, trackerToCreate);
        otherTrackingId = otherCreatedTracker.getTrackingId();

        manager.onTrackerSteps().restoreTrackerAndExpectError(APP_ID, trackingId, HUAWEI_LINK_ID_CONFLICT);
    }

    @After
    public void teardown() {
        manager.onTrackerSteps().removeTrackerAndIgnoreResult(APP_ID, trackingId);
        manager.onTrackerSteps().removeTrackerAndIgnoreResult(APP_ID, otherTrackingId);
    }
}
