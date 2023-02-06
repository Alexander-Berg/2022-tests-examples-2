package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import java.util.Collection;
import java.util.Set;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.appmetrica.actions.EditAction;
import ru.yandex.autotests.metrika.appmetrica.data.Partner;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.metrika.mobmet.model.redirect.AppDeepLink;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.segments.apps.misc.MobPlatform;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.DOUBLECLICK;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.FACEBOOK;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.HUAWEI_ADS;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.changeHuaweiLinkId;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.changeTiktokAppId;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.changeTrackerName;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.changeTrackerPostbackContents;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.changeTrackerPostbacks;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.changeTrackerToFallback;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.changeTrackerToMultiplatform;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultDeepLink;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultMultiplatformTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultPostback;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTargetUrl;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.defaultTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.huaweiAdsTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.oldPostback;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.postPostback;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.randomHuaweiLinkId;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.remarketingMyTargetTracker;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.tiktokTrackerWithPostback;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.trackerWithOmniPostback;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.trackerWithPostPostback;

/**
 * Created by graev on 07/12/2016.
 */

@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.EDIT,
})
@Title("Редактирование трекера")
@RunWith(Parameterized.class)
public final class EditTrackerTest {

    private static final UserSteps owner = UserSteps.onTesting(SIMPLE_USER);

    private static final GrantCreator GRANTS = forUser(SIMPLE_USER_2);

    private static final Set<Long> NO_TARGET_URL_PARTNERS = Set.of(
            FACEBOOK.get(Partner.ID),
            DOUBLECLICK.get(Partner.ID),
            HUAWEI_ADS.get(Partner.ID));

    private static final Set<Long> NO_DEEPLINK_PARTNERS = Set.of(
            DOUBLECLICK.get(Partner.ID),
            HUAWEI_ADS.get(Partner.ID));

    @Parameterized.Parameter
    public CampaignWrapper trackerToAdd;

    @Parameterized.Parameter(1)
    public EditAction<Campaign, Campaign> editAction;

    @Parameterized.Parameter(2)
    public User operator;

    @Parameterized.Parameter(3)
    public GrantWrapper grant;

    private UserSteps operatorSteps;

    private Campaign expectedTracker;

    private Campaign addedTracker;

    private Campaign editedTracker;

    private Long appId;

    @Parameterized.Parameters(name = "{0}. {1}. Пользователь {2}. {3}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(defaultTracker(), changeTrackerName(), SIMPLE_USER))
                .add(param(defaultTracker(), changeTrackerPostbacks(), SIMPLE_USER))
                .add(param(defaultTracker(), changeTrackerPostbacks(oldPostback(), oldPostback()), SIMPLE_USER))
                .add(param(defaultTracker(), changeTrackerPostbacks(defaultPostback(), postPostback()), SIMPLE_USER))
                .add(param(trackerWithPostPostback(), changeTrackerPostbackContents(), SIMPLE_USER))
                .add(param(trackerWithOmniPostback(), changeTrackerPostbackContents(), SIMPLE_USER))
                .add(param(defaultTracker(), changeTrackerToMultiplatform(owner), SIMPLE_USER))
                .add(param(remarketingMyTargetTracker(), changeTrackerName(), SIMPLE_USER))
                .add(param(remarketingMyTargetTracker(), changeTrackerPostbacks(), SIMPLE_USER))
                .add(param(defaultMultiplatformTracker(), changeTrackerName(), SIMPLE_USER))
                .add(param(defaultMultiplatformTracker(), changeTrackerToFallback(owner), SIMPLE_USER))
                .add(param(defaultTracker(), changeTrackerName(), SIMPLE_USER_2, GRANTS.agencyEditGrant())) // Агентский доступ
                .add(param(tiktokTrackerWithPostback(), changeTiktokAppId(), SIMPLE_USER))
                .add(param(huaweiAdsTracker(), changeHuaweiLinkId(randomHuaweiLinkId()), SIMPLE_USER))
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
            if (!NO_TARGET_URL_PARTNERS.contains(trackerToAdd.getCampaign().getPartnerId())) {
                // Загрузим target Url
                AppTargetUrl targetUrl = owner.onTrackerSteps().getOrCreateTargetUrl(appId, defaultTargetUrl(platform.getName()));
                platform.setTargetUrlId(targetUrl.getId());
            }

            // Загрузим deeplink
            if (platform.getName() != MobPlatform.FALLBACK &&
                    !NO_DEEPLINK_PARTNERS.contains(trackerToAdd.getCampaign().getPartnerId())) {
                AppDeepLink deeplink = owner.onTrackerSteps().getOrCreateDeepLink(appId, defaultDeepLink(platform.getName()));
                platform.setDeepLinkId(deeplink.getId());
            }
        });
        addedTracker = owner.onTrackerSteps().createTracker(appId, trackerToAdd);
        addedTracker.setUpdateTime(null);

        // Редактируем трекер
        expectedTracker = editAction.edit(addedTracker);
        editedTracker = operatorSteps.onTrackerSteps()
                .editTracker(appId, addedTracker.getTrackingId(), new CampaignWrapper(editAction.getUpdate(addedTracker)));
        editedTracker.setUpdateTime(null);
    }

    @Test
    public void checkTrackerInfo() {
        assertThat("отредактированный трекер эквивалентен измененному", editedTracker,
                equivalentTo(expectedTracker));
    }

    @Test
    public void checkActualTrackerInfo() {
        final Campaign actual = operatorSteps.onTrackerSteps().getTracker(appId, editedTracker.getTrackingId());
        assertThat("отредактированный трекер эквивалентен измененному", actual,
                equivalentTo(expectedTracker));
    }

    @After
    public void teardown() {
        owner.onTrackerSteps().removeTrackerAndIgnoreResult(appId, addedTracker.getTrackingId());

        addedTracker.getPlatforms().forEach(
                platform -> owner.onTrackerSteps().deleteTargetUrlAndIgnoreResult(appId, platform.getTargetUrlId()));

        if (grant.getGrant() != null) {
            owner.onGrantSteps().deleteGrantIgnoringResult(appId, grant.getGrant().getUserLogin());
        }

        owner.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    public static Object[] param(Campaign campaign, EditAction<Campaign, Campaign> editAction, User user) {
        return param(campaign, editAction, user, null);
    }

    public static Object[] param(Campaign campaign, EditAction<Campaign, Campaign> editAction, User user, MobmetGrantE grant) {
        return toArray(new CampaignWrapper(campaign), editAction, user, new GrantWrapper(grant));
    }

}
