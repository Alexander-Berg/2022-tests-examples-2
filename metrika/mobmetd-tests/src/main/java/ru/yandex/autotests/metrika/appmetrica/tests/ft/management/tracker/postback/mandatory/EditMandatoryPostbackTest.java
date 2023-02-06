package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker.postback.mandatory;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.appmetrica.errors.ManagementError;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.Postback;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.singletonList;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.anotherPostbackUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTrackerWithMandatoryPostback;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.single;

/**
 * Created by graev on 12/04/2017.
 */
@Features(Requirements.Feature.Management.Tracker.MANDATORY_POSTBACK)
@Stories({
        Requirements.Story.Tracker.Postback.MandatoryPostback.EDIT,
})
@Title("Редактирование обязательного постбека")
public final class EditMandatoryPostbackTest {

    private final UserSteps userSteps = UserSteps.onTesting(SIMPLE_USER);

    private Campaign addedTracker;

    private AppTargetUrl targetUrl;

    private Long appId;

    private CampaignWrapper trackerUpdate;

    @Before
    public void setup() {
        // Добавляем приложение
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        // Создаем трекер
        final CampaignWrapper trackerToAdd = new CampaignWrapper(defaultTrackerWithMandatoryPostback());
        targetUrl = userSteps.onTrackerSteps().getOrCreateTargetUrl(appId, defaultTargetUrl());
        trackerToAdd.getCampaign().getPlatforms().get(0).setTargetUrlId(targetUrl.getId());
        addedTracker = userSteps.onTrackerSteps().createTracker(appId, trackerToAdd);
        final Postback addedPostback = single(addedTracker.getPostbacks());

        // Готовим обновленную кампанию
        final Postback postbackUpdate = addedPostback.withUrl(anotherPostbackUrl());
        trackerUpdate = new CampaignWrapper(addedTracker.withPostbacks(singletonList(postbackUpdate)));
    }

    @Test
    public void checkPostbackUpdateFails() {
        userSteps.onTrackerSteps().editTrackerAndExpectError(appId, trackerUpdate.getCampaign().getTrackingId(),
                trackerUpdate, ManagementError.MANDATORY_POSTBACK);
    }

    @After
    public void teardown() {
        userSteps.onTrackerSteps().removeTrackerAndIgnoreResult(appId, addedTracker.getTrackingId());
        userSteps.onTrackerSteps().deleteTargetUrlAndIgnoreResult(appId, targetUrl.getId());
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}


