package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker.postback.mandatory;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
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
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.mandatoryPostback;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.single;

/**
 * Created by graev on 12/04/2017.
 */
@Features(Requirements.Feature.Management.Tracker.MANDATORY_POSTBACK)
@Stories({
        Requirements.Story.Tracker.Postback.MandatoryPostback.ADD,
})
@Title("Создание обязательного постбека")
public final class AddMandatoryPostbackTest {

    private final UserSteps userSteps = UserSteps.onTesting(SIMPLE_USER);

    private CampaignWrapper trackerToAdd;

    private Campaign addedTracker;

    private AppTargetUrl targetUrl;

    private Long appId;

    private Postback addedPostback;

    private Postback expectedPostback;

    @Before
    public void setup() {
        // Добавляем приложение
        Application addedApplication = userSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        // Создаем трекер
        trackerToAdd = new CampaignWrapper(defaultTracker());
        targetUrl = userSteps.onTrackerSteps().getOrCreateTargetUrl(appId, defaultTargetUrl());
        trackerToAdd.getCampaign().getPlatforms().get(0).setTargetUrlId(targetUrl.getId());
        addedTracker = userSteps.onTrackerSteps().createTracker(appId, trackerToAdd);

        // Создаем обязательный постбек обновляя трекер
        expectedPostback = mandatoryPostback();
        final Campaign editedTracker = addedTracker.withPostbacks(singletonList(expectedPostback));
        final Campaign updated = userSteps.onTrackerSteps().editTracker(appId, editedTracker.getTrackingId(),
                new CampaignWrapper(editedTracker));
        addedPostback = single(updated.getPostbacks());
    }

    @Test
    public void checkCreatedPostbackInfo() {
        assertThat("добавленный постбек эквивалентен ожидаемому", addedPostback,
                equivalentTo(expectedPostback));
    }

    @Test
    public void checkActualPostbackInfo() {
        final Postback actualPostback = userSteps.onTrackerSteps().getSinglePostback(appId, addedTracker.getTrackingId());
        assertThat("актуальный постбек эквивалентен ожидаемому", actualPostback,
                equivalentTo(expectedPostback));
    }

    @After
    public void teardown() {
        userSteps.onTrackerSteps().removeTrackerAndIgnoreResult(appId, addedTracker.getTrackingId());
        userSteps.onTrackerSteps().deleteTargetUrlAndIgnoreResult(appId, targetUrl.getId());
        userSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }
}

