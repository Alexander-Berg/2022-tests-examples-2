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
@Title("???????????????? ??????????????")
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
                        "?????????????????????? ????????????",
                        TestData::defaultTracker,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        ORDINARY))
                .add(param(
                        "???????????? ?? ?????????????????????? ??????????????????????",
                        TestData::defaultMultiplatformTracker,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        ORDINARY))
                .add(param(
                        "?????????????????? ?????????????? ?????? ?????????????????? ????????????????",
                        TestData::defaultTracker,
                        TestData::defaultTargetUrl,
                        WITHOUT_DEEP_LINK,
                        ORDINARY,
                        SIMPLE_USER,
                        SIMPLE_USER_2,
                        forUser(SIMPLE_USER_2).agencyEditGrant())) // ?????????????????? ????????????
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
                        "Facebook ?? ??????????????????",
                        TestData::facebookTracker,
                        WITHOUT_TARGET_URL,
                        TestData::defaultDeepLink,
                        FACEBOOK))
                .add(param(
                        "Facebook ?? decryption key",
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
                        "???????????? ?? ecom ??????????????????",
                        TestData::trackerWithEcomPostback,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        ORDINARY))
                .add(param(
                        "???????????? ?? revenue ??????????????????",
                        TestData::trackerWithRevenuePostback,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        ORDINARY))
                .add(param(
                        "???????????? ?? post ??????????????????",
                        TestData::trackerWithPostPostback,
                        TestData::defaultTargetUrl,
                        TestData::defaultDeepLink,
                        ORDINARY))
                .add(param(
                        "???????????? ?? omni ??????????????????",
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

        // ?????????????????? ????????????????????
        Application addedApplication = ownerSteps.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();

        // ???????????? ?????????? ???????? ??????????
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
                    // ?????????? id target url ???????????? ?????????????????????????? ???????????????????? ???? ???????????? ???? ????????
                    platformsToAdd.get(platform.getName()).setTargetUrlId(targetUrl.getId());
                });

        expectedTracker.getPlatforms().stream()
                .filter(platform -> platform.getDeepLink() != null)
                .forEach(platform -> {
                    AppDeepLink deepLink = operatorSteps.onTrackerSteps().getOrCreateDeepLink(appId, platform.getDeepLink());
                    platform.setDeepLinkId(deepLink.getId());
                    // ?????????? id deep link-?? ???????????? ?????????????????????????? ???????????????????? ???? ???????????? ???? ????????
                    platformsToAdd.get(platform.getName()).setDeepLinkId(deepLink.getId());
                });

        // ?????????????? ????????????
        addedTracker = operatorSteps.onTrackerSteps().createTracker(appId, trackerToAdd);
    }

    @Test
    public void checkCreatedTrackerInfo() {
        assertThat("?????????????????????? ???????????? ???????????????????????? ????????????????????", addedTracker,
                equivalentTo(expectedTracker));
    }

    @Test
    public void checkActualTrackerInfo() {
        final Campaign actual = operatorSteps.onTrackerSteps().getTracker(appId, addedTracker.getTrackingId());
        assertThat("?????????????????????? ???????????? ???????????????????????? ??????????????????????", actual,
                equivalentTo(expectedTracker));
    }

    @Test
    public void checkTrackerInList() {
        final List<Campaign> trackers = operatorSteps.onTrackerSteps().getTrackerList(appId);
        // ?? ???????????? ???????????????? ?????? ??????????????????
        Campaign expected = expectedTracker.withPostbacks(null);
        assertThat("???????????? ???????????????? ???????????????? ????????????, ?????????????????????????? ????????????????????", trackers,
                hasItem(equivalentTo(expected)));
    }

    @Test
    public void checkEmptyMetrics() {
        final List<CampaignMetrics> actual = operatorSteps.onTrackerSteps()
                .getTrackerMetrics(Collections.singletonList(addedTracker.getTrackingId()));
        final List<CampaignMetrics> expected = Collections.singletonList(
                new CampaignMetrics().withTrackingId(addedTracker.getTrackingId()));
        assertThat("???? ???????????? ?????????????? ?????? ????????????????????", actual, equivalentTo(expected));
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
     * ???????????????? ???? ???????? ??????????????, ?? ???????????? ????????????????, ?????? ???? ??????????????????, ???????????? ?????? ????????????, ?????????????? ???? ???????????????? ??????
     * ???????????? ?? ?????????????????? ???????????? ?????????? ????????????, ???? ???????????? ?????? ???????? ?????????????????????? ?? ???? ?????????????? ?? ???????????? ??????????????????????
     * ???????????? ????????.
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

        // ?????????????????? ???? ?????????????????? ???????????? ??????????, ?????? ???? ???? ???????????????????? ???? ???? ????????????
        return toArray(name, new CampaignWrapper(request), expected, owner, user, new GrantWrapper(grant));
    }
}
