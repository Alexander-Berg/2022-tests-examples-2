package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.autotests.metrika.appmetrica.wrappers.CampaignWrapper;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.metrika.mobmet.model.redirect.AppDeepLink;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.CampaignMetrics;
import ru.yandex.metrika.mobmet.model.redirect.CampaignPlatform;
import ru.yandex.metrika.segments.apps.misc.MobPlatform;
import ru.yandex.metrika.segments.apps.misc.PartnerType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.CoreMatchers.hasItem;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER_2;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.GrantCreator.forUser;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.getDefaultApplication;
import static ru.yandex.metrika.segments.apps.misc.PartnerType.ADWORDS;
import static ru.yandex.metrika.segments.apps.misc.PartnerType.DIRECT;
import static ru.yandex.metrika.segments.apps.misc.PartnerType.DOUBLECLICK;
import static ru.yandex.metrika.segments.apps.misc.PartnerType.FACEBOOK;
import static ru.yandex.metrika.segments.apps.misc.PartnerType.HUAWEI_ADS;
import static ru.yandex.metrika.segments.apps.misc.PartnerType.MYTARGET;
import static ru.yandex.metrika.segments.apps.misc.PartnerType.ORDINARY;

/**
 * Created by graev on 02/12/2016.
 */
@Features(Requirements.Feature.Management.TRACKER)
@Stories({
        Requirements.Story.Tracker.ADD,
        Requirements.Story.Tracker.INFO,
        Requirements.Story.Tracker.LIST
})
@Title("Создание трекера")
@RunWith(Parameterized.class)
public final class AddTrackerTest {

    private static final Function<MobPlatform, AppTargetUrl> WITHOUT_TARGET_URL = platform -> null;
    private static final Function<MobPlatform, AppDeepLink> WITHOUT_DEEP_LINK = platform -> null;

    @Parameterized.Parameter
    public String name;

    @Parameterized.Parameter(1)
    public CampaignWrapper trackerToAdd;

    @Parameterized.Parameter(2)
    public Campaign expectedTracker;

    @Parameterized.Parameter(3)
    public User owner;

    @Parameterized.Parameter(4)
    public User operator;

    @Parameterized.Parameter(5)
    public GrantWrapper grant;

    private UserSteps ownerSteps;

    private UserSteps operatorSteps;

    private Campaign addedTracker;

    private Long appId;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(
                        "Стандартный трекер",
                        TestData::defaultTracker,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        ORDINARY))
                .add(param(
                        "Трекер с несколькими платформами",
                        TestData::defaultMultiplatformTracker,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        ORDINARY))
                .add(param(
                        "Видимость трекера под агентским доступом",
                        TestData::defaultTracker,
                        TestData::defaultTargetUrl,
                        WITHOUT_DEEP_LINK,
                        ORDINARY,
                        SIMPLE_USER,
                        SIMPLE_USER_2,
                        forUser(SIMPLE_USER_2).agencyEditGrant())) // Агентский доступ
                .add(param(
                        "Deprecated Google AdWords Tracker",
                        TestData::adwordsTrackerNoAppDeprecated,
                        TestData::defaultTargetUrl,
                        WITHOUT_DEEP_LINK,
                        ADWORDS))
                .add(param("Semi-new Google AdWords Tracker",
                        TestData::adwordsTrackerNoAppSemiNew,
                        TestData::defaultTargetUrl,
                        WITHOUT_DEEP_LINK,
                        ADWORDS))
                .add(param("Google AdWords Tracker",
                        TestData::adwordsTrackerNoApp,
                        WITHOUT_TARGET_URL,
                        WITHOUT_DEEP_LINK,
                        ADWORDS))
                .add(param("Google AdWords Tracker With New Postback",
                        TestData::adwordsTrackerNoAppWithNewPostback,
                        WITHOUT_TARGET_URL,
                        WITHOUT_DEEP_LINK,
                        ADWORDS))
                .add(param(
                        "MyTarget",
                        TestData::mytargetTracker,
                        TestData::defaultTargetUrl,
                        WITHOUT_DEEP_LINK,
                        MYTARGET))
                .add(param(
                        "Facebook с диплинком",
                        TestData::facebookTracker,
                        WITHOUT_TARGET_URL,
                        TestData::defaultDeepLink,
                        FACEBOOK))
                .add(param(
                        "Facebook с decryption key",
                        TestData::facebookTrackerWithDecryptionKey,
                        WITHOUT_TARGET_URL,
                        WITHOUT_DEEP_LINK,
                        FACEBOOK))
                .add(param(
                        "Huawei Ads",
                        TestData::huaweiAdsTracker,
                        WITHOUT_TARGET_URL,
                        WITHOUT_DEEP_LINK,
                        HUAWEI_ADS))
                .add(param(
                        "Direct",
                        TestData::directTracker,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        DIRECT))
                .add(param(
                        "Direct multiplatform",
                        TestData::remarketingDirectMultiplatformTracker,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        DIRECT))
                .add(param(
                        "DoubleClick",
                        TestData::doubleClickTracker,
                        WITHOUT_TARGET_URL,
                        WITHOUT_DEEP_LINK,
                        DOUBLECLICK
                ))
                .add(param("Remarketing",
                        TestData::remarketingMyTargetTracker,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        MYTARGET))
                .add(param("Remarketing with smartlinks",
                        TestData::remarketingWithSmartLinksTracker,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        ORDINARY))
                .add(param(
                        "Трекер с ecom постбэком",
                        TestData::trackerWithEcomPostback,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        ORDINARY))
                .add(param(
                        "Трекер с revenue постбэком",
                        TestData::trackerWithRevenuePostback,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        ORDINARY))
                .add(param(
                        "Трекер с post постбэком",
                        TestData::trackerWithPostPostback,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        ORDINARY))
                .add(param(
                        "Трекер с omni постбэком",
                        TestData::trackerWithOmniPostback,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        ORDINARY))
                .build();
    }

    @Before
    public void setup() {
        ownerSteps = UserSteps.onTesting(owner);
        operatorSteps = UserSteps.onTesting(operator);

        // Добавляем приложение
        Application addedApplication = ownerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        // Делаем грант если нужно
        if (grant.getGrant() != null) {
            ownerSteps.onGrantSteps().createGrant(appId, grant);
        }

        Map<MobPlatform, CampaignPlatform> platformsToAdd = trackerToAdd.getCampaign().getPlatforms().stream()
                .collect(Collectors.toMap(CampaignPlatform::getName, Function.identity()));

        expectedTracker.getPlatforms().stream()
                .filter(platform -> platform.getTargetUrl() != null)
                .forEach(platform -> {
                    AppTargetUrl targetUrl = operatorSteps.onTrackerSteps().getOrCreateTargetUrl(appId, platform.getTargetUrl());
                    platform.setTargetUrlId(targetUrl.getId());
                    // Кроме id target url ничего дополнительно передавать на сервер не надо
                    platformsToAdd.get(platform.getName()).setTargetUrlId(targetUrl.getId());
                });

        expectedTracker.getPlatforms().stream()
                .filter(platform -> platform.getDeepLink() != null)
                .forEach(platform -> {
                    AppDeepLink deepLink = operatorSteps.onTrackerSteps().getOrCreateDeepLink(appId, platform.getDeepLink());
                    platform.setDeepLinkId(deepLink.getId());
                    // Кроме id deep link-а ничего дополнительно передавать на сервер не надо
                    platformsToAdd.get(platform.getName()).setDeepLinkId(deepLink.getId());
                });

        // Создаем трекер
        addedTracker = operatorSteps.onTrackerSteps().createTracker(appId, trackerToAdd);
    }

    @Test
    public void checkCreatedTrackerInfo() {
        assertThat("добавленный трекер эквивалентен ожидаемому", addedTracker,
                equivalentTo(expectedTracker));
    }

    @Test
    public void checkActualTrackerInfo() {
        final Campaign actual = operatorSteps.onTrackerSteps().getTracker(appId, addedTracker.getTrackingId());
        assertThat("добавленный трекер эквивалентен актуальному", actual,
                equivalentTo(expectedTracker));
    }

    @Test
    public void checkTrackerInList() {
        final List<Campaign> trackers = operatorSteps.onTrackerSteps().getTrackerList(appId);
        // в списке трекеров нет постбеков
        Campaign expected = expectedTracker.withPostbacks(null);
        assertThat("список трекеров содержит трекер, эквивалентный ожидаемому", trackers,
                hasItem(equivalentTo(expected)));
    }

    @Test
    public void checkEmptyMetrics() {
        final List<CampaignMetrics> actual = operatorSteps.onTrackerSteps()
                .getTrackerMetrics(Collections.singletonList(addedTracker.getTrackingId()));
        final List<CampaignMetrics> expected = Collections.singletonList(
                new CampaignMetrics().withTrackingId(addedTracker.getTrackingId()));
        assertThat("по новому трекеру нет статистики", actual, equivalentTo(expected));
    }

    @After
    public void teardown() {
        if (addedTracker != null) {
            operatorSteps.onTrackerSteps().removeTrackerAndIgnoreResult(appId, addedTracker.getTrackingId());
        }

        expectedTracker.getPlatforms().stream()
                .filter(platform -> platform.getTargetUrl() != null)
                .forEach(platform -> ownerSteps.onTrackerSteps().deleteTargetUrlAndIgnoreResult(appId, platform.getTargetUrlId()));
        expectedTracker.getPlatforms().stream()
                .filter(platform -> platform.getDeepLink() != null)
                .forEach(platform -> ownerSteps.onTrackerSteps().deleteDeepLinkAndIgnoreResult(appId, platform.getDeepLinkId()));

        if (grant.getGrant() != null) {
            ownerSteps.onGrantSteps().deleteGrantIgnoringResult(appId, grant.getGrant().getUserLogin());
        }

        ownerSteps.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    public static Object[] param(String name,
                                 Supplier<Campaign> campaignSupplier,
                                 Function<MobPlatform, AppTargetUrl> targetUrlsSupplier,
                                 Function<MobPlatform, AppDeepLink> deepLinksSupplier,
                                 PartnerType targetPartnerType) {
        return param(name, campaignSupplier, targetUrlsSupplier, deepLinksSupplier, targetPartnerType, SIMPLE_USER, SIMPLE_USER, null);
    }

    /**
     * Передаём не сами трекеры, а скорее описание, как их создавать, потому что трекер, который мы передаём как
     * запрос и ожидаемый трекер очень похожи, но полями все таки различаются и не хочется в запрос прокидывать
     * лишние поля.
     */
    public static Object[] param(String name,
                                 Supplier<Campaign> campaignSupplier,
                                 Function<MobPlatform, AppTargetUrl> targetUrlsSupplier,
                                 Function<MobPlatform, AppDeepLink> deepLinksSupplier,
                                 PartnerType targetPartnerType,
                                 User user) {
        return param(name, campaignSupplier, targetUrlsSupplier, deepLinksSupplier, targetPartnerType, user, user, null);
    }

    public static Object[] param(String name,
                                 Supplier<Campaign> campaignSupplier,
                                 Function<MobPlatform, AppTargetUrl> targetUrlsSupplier,
                                 Function<MobPlatform, AppDeepLink> deepLinksSupplier,
                                 PartnerType targetPartnerType,
                                 User owner,
                                 User user,
                                 MobmetGrantE grant) {
        Campaign request = campaignSupplier.get();

        Campaign expected = campaignSupplier.get();
        expected.setName(request.getName());
        expected.getPlatforms().forEach(platform -> {
            platform.setTargetUrl(targetUrlsSupplier.apply(platform.getName()));
            if (platform.getName() != MobPlatform.FALLBACK) {
                platform.setDeepLink(deepLinksSupplier.apply(platform.getName()));
            }
        });
        expected.setPartnerType(targetPartnerType);

        // Стараемся не заполнять лишних полей, что бы не отправлять их на сервер
        return toArray(name, new CampaignWrapper(request), expected, owner, user, new GrantWrapper(grant));
    }
}
