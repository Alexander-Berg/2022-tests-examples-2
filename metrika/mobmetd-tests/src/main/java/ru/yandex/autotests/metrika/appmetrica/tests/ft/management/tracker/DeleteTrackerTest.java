package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import java.util.Collection;
import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.errors.ManagementError;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.hasItem;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.Matchers.hasProperty;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultMultiplatformTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.trackerWithOmniPostback;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.trackerWithPostPostback;

/**
 * Created by graev on 07/12/2016.
 */
@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.DELETE,
})
@Title("Удаление трекера")
@RunWith(Parameterized.class)
public final class DeleteTrackerTest {

    private final UserSteps owner = UserSteps.onTesting(SIMPLE_USER);

    private static final GrantCreator GRANTS = forUser(SIMPLE_USER_2);

    @Parameterized.Parameter
    public CampaignWrapper trackerToAdd;

    @Parameterized.Parameter(1)
    public User operator;

    @Parameterized.Parameter(2)
    public GrantWrapper grant;

    private UserSteps operatorSteps;

    private Campaign addedTracker;

    private Long appId;

    @Parameterized.Parameters(name = "{0}. Пользователь {1}. {2}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(defaultTracker(), SIMPLE_USER))
                .add(param(defaultMultiplatformTracker(), SIMPLE_USER))
                .add(param(trackerWithPostPostback(), SIMPLE_USER))
                .add(param(trackerWithOmniPostback(), SIMPLE_USER))
                .add(param(defaultTracker(), SIMPLE_USER_2, GRANTS.agencyEditGrant())) // Агентский доступ
                .build();
    }

    @Before
    public void setup() {
        operatorSteps = UserSteps.onTesting(operator);

        // Добавляем приложение
        Application addedApplication = owner.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        // Делаем грант если нужно
        if (grant.getGrant() != null) {
            owner.onGrantSteps().createGrant(appId, grant);
        }

        // Создаем трекер
        trackerToAdd.getCampaign().getPlatforms().forEach(platform -> {
            AppTargetUrl targetUrl = owner.onTrackerSteps().getOrCreateTargetUrl(appId, defaultTargetUrl(platform.getName()));
            platform.setTargetUrlId(targetUrl.getId());
        });
        addedTracker = owner.onTrackerSteps().createTracker(appId, trackerToAdd);

        // Удаляем трекер
        operatorSteps.onTrackerSteps().removeTracker(appId, addedTracker.getTrackingId());
    }

    @Test
    public void checkTrackerIsNotInList() {
        final List<Campaign> campaigns = operatorSteps.onTrackerSteps().getTrackerList(appId);
        assertThat("удаленный трекер не найден в списке трекеров", campaigns,
                not(hasItem(hasProperty("trackingId", equalTo(addedTracker.getTrackingId())))));
    }

    @Test
    public void checkTrackerIsNotFound() {
        operatorSteps.onTrackerSteps()
                .getTrackerAndExpectError(appId, addedTracker.getTrackingId(), ManagementError.TRACKER_NOT_FOUND);
    }

    @After
    public void teardown() {
        owner.onTrackerSteps().removeTrackerAndIgnoreResult(appId, addedTracker.getTrackingId());

        addedTracker.getPlatforms()
                .forEach(platform -> owner.onTrackerSteps().deleteTargetUrlAndIgnoreResult(appId, platform.getTargetUrlId()));

        if (grant.getGrant() != null) {
            owner.onGrantSteps().deleteGrantIgnoringResult(appId, grant.getGrant().getUserLogin());
        }

        owner.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    public static Object[] param(Campaign campaign, User user) {
        return param(campaign, user, null);
    }

    public static Object[] param(Campaign campaign, User user, MobmetGrantE grant) {
        return toArray(new CampaignWrapper(campaign), user, new GrantWrapper(grant));
    }
}
