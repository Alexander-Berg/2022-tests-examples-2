package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import java.util.Collection;

import com.google.common.collect.ImmutableList;
import com.rits.cloning.Cloner;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.actions.EditAction;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.redirect.AppDeepLink;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.errors.ManagementError.REMARKETING_TRACKER_EDITING;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultDeepLink;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.remarketingMyTargetTracker;

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.EDIT,
})
@Title("Редактирование трекера (негативный)")
@RunWith(Parameterized.class)
public final class EditTrackerNegativeTest {

    private static final UserSteps owner = UserSteps.onTesting(SIMPLE_USER);

    @Parameterized.Parameter
    public CampaignWrapper trackerToAdd;

    @Parameterized.Parameter(1)
    public EditAction<Campaign, Campaign> editAction;

    @Parameterized.Parameter(2)
    public User operator;

    @Parameterized.Parameter(3)
    public IExpectedError expectedError;

    private UserSteps operatorSteps;

    private Campaign addedTracker;

    private Long appId;

    @Parameterized.Parameters(name = "{0}. {1}. Пользователь {2}. {3}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(remarketingMyTargetTracker(), disableRemarketingForTracker(), SIMPLE_USER, REMARKETING_TRACKER_EDITING))
                .build();
    }

    @Before
    public void setup() {
        operatorSteps = UserSteps.onTesting(operator);

        // Добавляем приложение
        Application addedApplication = owner.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        // Создаем трекер
        trackerToAdd.getCampaign().getPlatforms().forEach(platform -> {
            // Загрузим target Url
            AppTargetUrl targetUrl = owner.onTrackerSteps().getOrCreateTargetUrl(appId, defaultTargetUrl(platform.getName()));
            platform.setTargetUrlId(targetUrl.getId());

            // Загрузим deeplink
            AppDeepLink deeplink = owner.onTrackerSteps().getOrCreateDeepLink(appId, defaultDeepLink(platform.getName()));
            platform.setDeepLinkId(deeplink.getId());
        });
        addedTracker = owner.onTrackerSteps().createTracker(appId, trackerToAdd);
    }

    @Test
    public void testTrackerEditFails() {
        operatorSteps.onTrackerSteps().editTrackerAndExpectError(
                appId,
                addedTracker.getTrackingId(),
                new CampaignWrapper(editAction.getUpdate(addedTracker)),
                expectedError);
    }

    @After
    public void teardown() {
        owner.onTrackerSteps().removeTrackerAndIgnoreResult(appId, addedTracker.getTrackingId());

        addedTracker.getPlatforms().forEach(
                platform -> owner.onTrackerSteps().deleteTargetUrlAndIgnoreResult(appId, platform.getTargetUrlId()));

        owner.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    public static Object[] param(Campaign campaign, EditAction<Campaign, Campaign> editAction, User user, IExpectedError expectedError) {
        return toArray(new CampaignWrapper(campaign), editAction, user, expectedError);
    }

    /**
     * Не уносим в TestData, поскольку здесь описываются заведомо неразрешённые действия над объектами.
     */
    private static EditAction<Campaign, Campaign> disableRemarketingForTracker() {
        return new EditAction<Campaign, Campaign>("Отключить ремаркетинг у трекера") {
            @Override
            public Campaign getUpdate(Campaign source) {
                return edit(source);
            }

            @Override
            public Campaign edit(Campaign source) {
                return new Cloner().deepClone(source)
                        .withRemarketingEnabled(false);
            }
        };
    }

}
