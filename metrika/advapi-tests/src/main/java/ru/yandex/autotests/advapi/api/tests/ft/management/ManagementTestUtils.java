package ru.yandex.autotests.advapi.api.tests.ft.management;

import org.joda.time.LocalDate;
import org.joda.time.format.DateTimeFormat;
import ru.yandex.advapi.V1ManagementAdvertiserAdvertiserIdCampaignsPOSTRequestSchema;
import ru.yandex.advapi.InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierPOSTSchema;
import ru.yandex.advapi.V1ManagementAdvertisersPOSTRequestSchema;
import ru.yandex.autotests.advapi.data.users.User;
import ru.yandex.autotests.advapi.parameters.MultiplierParameters;
import ru.yandex.autotests.advapi.steps.UserSteps;
import ru.yandex.metrika.adv.api.management.advertiser.AdvertiserPermission;
import ru.yandex.metrika.adv.api.management.advertiser.external.AdvertiserInfo;
import ru.yandex.metrika.adv.api.management.advertiser.external.AdvertiserSettings;
import ru.yandex.metrika.adv.api.management.campaign.CampaignStatus;
import ru.yandex.metrika.adv.api.management.campaign.ViewabilityStandard;
import ru.yandex.metrika.adv.api.management.campaign.external.CampaignInfo;
import ru.yandex.metrika.adv.api.management.campaign.external.CampaignSettingsIn;
import ru.yandex.metrika.adv.api.management.campaign.external.CampaignSettingsOut;
import ru.yandex.metrika.adv.api.management.creative.Creative;
import ru.yandex.metrika.adv.api.management.landing.Landing;
import ru.yandex.metrika.adv.api.management.placement.PlacementType;
import ru.yandex.metrika.adv.api.management.placement.PricingModel;
import ru.yandex.metrika.adv.api.management.placement.external.PlacementIn;
import ru.yandex.metrika.adv.api.management.placement.external.PlacementOut;
import ru.yandex.metrika.adv.api.management.site.Site;
import ru.yandex.metrika.adv.api.management.site.SiteType;
import ru.yandex.metrika.api.management.client.counter.CounterIdEnhanced;
import ru.yandex.metrika.api.management.client.grants.Grant;
import ru.yandex.metrika.rbac.Permission;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
import java.util.Random;
import java.util.stream.Collectors;

import static java.util.Arrays.asList;
import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static ru.yandex.autotests.advapi.data.users.Users.READ_GUEST;
import static ru.yandex.autotests.advapi.data.users.Users.WRITE_GUEST;

public class ManagementTestUtils {

    public static Landing LANDING_172 = new Landing()
            .withLandingId(172L)
            .withName("example.com")
            .withUrl("https://example.com");

    public static Site SITE_2 = new Site()
            .withName("Яндекс — поисковая система и интернет-портал")
            .withSiteId(2L)
            .withUrl("yandex.ru")
            .withSiteType(SiteType.SITE)
            .withTracking(true)
            .withViewability(true);

    public static PlacementOut PLACEMENT_268_BEAN = new PlacementOut()
            .withName("test_placement")
            .withPlacementType(PlacementType.BANNER)
            .withPricingModel(PricingModel.CPM)
            .withVolume(0L)
            .withCost(0.0)
            .withCreatives(singletonList(new Creative().withComment("Креатив 1").withCreativeId(73L)))
            .withPlacementId(268L)
            .withSite(new Site()
                    .withSiteId(11417L)
                    .withName("\"AstroHelper.ru\" - Твой астрологический помощник")
                    .withUrl("astrohelper.ru")
                    .withTracking(true)
                    .withViewability(true))
            .withLanding(new Landing()
                    .withLandingId(166L)
                    .withName("example.com")
                    .withUrl("https://example.com"))
            .withTracking(false)
            .withViewability(false);

    public static AdvertiserSettings ADVERTISER_196_BEAN;

    static {
        try {
            ADVERTISER_196_BEAN = new AdvertiserSettings()
                    .withAdvertiserId(196L)
                    .withName("admetrica_test_adv_group_1")
                    .withPermission(AdvertiserPermission.OWN)
                    .withGrants(asList(
                            new Grant()
                                    .withUserLogin("read-guest")
                                    .withCreatedAt(new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss").parse("2019-04-30T17:48:11+03:00"))
                                    .withComment("")
                                    .withPermission(Permission.VIEW),
                            new Grant()
                                    .withUserLogin("write-guest")
                                    .withCreatedAt(new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss").parse("2019-04-30T17:48:11+03:00"))
                                    .withComment("")
                                    .withPermission(Permission.EDIT)
                    ))
                    .withCreateTime("2019-02-20 18:50:58")
                    .withOwner("simple-admetrika-user-1")
                    .withPostClickDays(30L)
                    .withPostViewDays(90L);
        } catch (ParseException e) {
            throw new RuntimeException(e);
        }
    }

    public static AdvertiserInfo ADVERTISER_INFO_196_BEAN = new AdvertiserInfo()
            .withAdvertiserId(196L)
            .withName("admetrica_test_adv_group_1")
            .withPermission(AdvertiserPermission.OWN)
            .withCreateTime("2019-02-20 18:50:58")
            .withOwner("simple-admetrika-user-1")
            .withGoalsCnt(0L)
            .withLandingsCnt(1L);

    public static AdvertiserInfo ADVERTISER_INFO_202_BEAN = new AdvertiserInfo()
            .withAdvertiserId(202L)
            .withName("admetrica_test_adv_group_1_adv_2")
            .withPermission(AdvertiserPermission.VIEW)
            .withCreateTime("2019-02-21 13:50:30")
            .withOwner("simple-admetrika-user-1")
            .withGoalsCnt(0L)
            .withLandingsCnt(1L);

    public static CampaignSettingsOut CAMPAIGN_256_BEAN = new CampaignSettingsOut()
            .withName("test_campaign_group_1")
            .withDateStart("2019-02-20")
            .withDateEnd("2029-02-28")
            .withStatus(CampaignStatus.ACTIVE)
            .withViewabilityStandard(ViewabilityStandard.YANDEX)
            .withPlanImpressions(1000000L)
            .withPlanClicks(100000L)
            .withGoalPlans(emptyList())
            .withGoals(emptyList())
            .withCampaignId(256L)
            .withCreateTime("2019-02-20 18:57:10")
            .withPlacements(singletonList(PLACEMENT_268_BEAN))
            .withPlanCtr(0.1)
            .withPlanCpm(1.0)
            .withPlanCpc(1.0);

    public static CampaignInfo CAMPAIGN_INFO_256_BEAN = new CampaignInfo()
            .withCampaignId(256L)
            .withAdvertiserId(196L)
            .withCampaignName("test_campaign_group_1")
            .withAdvertiserName("admetrica_test_adv_group_1")
            .withDateStart("2019-02-20")
            .withDateEnd("2029-02-28")
            .withStatus(CampaignStatus.ACTIVE)
            .withCreateTime("2019-02-20 18:50:58")
            .withOwner("simple-admetrika-user-1");

    public static AdvertiserSettings createSimpleAdvertiser(User user) {
        return createAdvertiser(user, getAdvertiserSettings().withGrants(asList(
                new Grant().withUserLogin(READ_GUEST.toString()).withPermission(Permission.VIEW),
                new Grant().withUserLogin(WRITE_GUEST.toString()).withPermission(Permission.EDIT)
        )));
    }

    public static AdvertiserSettings createAdvertiser(User user, AdvertiserSettings settings) {
        V1ManagementAdvertisersPOSTRequestSchema body = new V1ManagementAdvertisersPOSTRequestSchema().withAdvertiser(settings);
        return UserSteps.withUser(user).onAdvertisersSteps().addAdvertisersAndExpectSuccess(body).getAdvertiser();
    }

    public static double getGrantMultiplier(User user, long advertiserId) {
        return UserSteps.withUser(user).onAdvertisersSteps().getAdvertiserGrantMultiplierAndExpectSuccess(advertiserId).getMultiplier();
    }

    public static double setGrantMultiplier(User user, long advertiserId, double multiplier) {
        InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierPOSTSchema body = new InternalV1ManagementAdvertiserAdvertiserIdGrantMultiplierPOSTSchema();
        MultiplierParameters parameters = new MultiplierParameters(multiplier);
        return UserSteps.withUser(user).onAdvertisersSteps().setAdvertiserGrantMultiplierAndExpectSuccess(
                advertiserId,
                body,
                parameters
        ).getMultiplier();
    }

    public static double deleteGrantMultiplier(User user, long advertiserId) {
        return UserSteps.withUser(user).onAdvertisersSteps().deleteAdvertiserGrantMultiplierAndExpectSuccess(
                advertiserId
        ).getMultiplier();
    }

    public static CampaignSettingsIn getPlainCampaignWithName(String name) {
        return new CampaignSettingsIn()
                .withName(name)
                .withPlacements(Collections.singletonList(getSimplePlacement()))
                .withDateStart(DateTimeFormat.forPattern("yyyy-MM-dd").print(LocalDate.now()))
                .withDateEnd(DateTimeFormat.forPattern("yyyy-MM-dd").print(LocalDate.now().plusDays(7)))
                .withViewabilityStandard(ViewabilityStandard.YANDEX)
                .withStatus(CampaignStatus.ACTIVE);
    }

    public static PlacementIn getSimplePlacement() {
        return new PlacementIn()
                .withName("placement_name_" + new SimpleDateFormat("yyyyMMddHHmmssSSS").format(new Date()))
                .withLandingId(172L)
                .withPlacementType(PlacementType.BANNER)
                .withPricingModel(PricingModel.CPC)
                .withSiteId(2L)
                .withCreatives(Collections.singletonList(new Creative().withComment("creative name")))
                .withCost(1d)
                .withVolume(10L);
    }

    public static CampaignSettingsIn getPlainCampaign() {
        return getPlainCampaignWithName("test_campaign_" + new SimpleDateFormat("yyyyMMddHHmmssSSS").format(new Date()))
                .withPlanCpc(9.9)
                .withPlanCpm(5.5)
                .withPlanCtr(1.1)
                .withPlanClicks(199L)
                .withPlanImpressions(1000L);
    }

    public static CampaignSettingsOut createBaseCampaign(User user, long advertiserId) {
        return UserSteps.withUser(user).onCampaignsSteps().addCampaignAndExpectSuccess(advertiserId, new V1ManagementAdvertiserAdvertiserIdCampaignsPOSTRequestSchema().withCampaign(getPlainCampaign())).getCampaign();
    }

    public static AdvertiserSettings getAdvertiserSettings() {
        return new AdvertiserSettings()
                .withName("test_advertiser_" + new SimpleDateFormat("yyyyMMddHHmmssSSS").format(new Date()))
                .withCounters(Arrays.asList(new CounterIdEnhanced().withCounterId(15L), new CounterIdEnhanced().withCounterId(17L)));
    }

    public static AdvertiserSettings getAdvertiserSettings(User grantee, Permission permission) {
        return getAdvertiserSettings()
                .withGrants(singletonList(
                        new Grant()
                                .withUserLogin(grantee.toString())
                                .withPermission(permission)
                                .withCreatedAt(new Date())
                ));
    }

    public static AdvertiserSettings getAdvertiserSettings(User grantee, Permission permission, long postClickDays, long postViewDays) {
        return getAdvertiserSettings(grantee, permission).withPostClickDays(postClickDays).withPostViewDays(postViewDays);
    }

    public static String getUpdateName(String entity) {
        return "test_" + entity + "_updated_" + new SimpleDateFormat("yyyyMMddHHmmssSSS").format(new Date());
    }

    public static String getTooLongName() {
        return new Random().ints(257).mapToObj(String::valueOf).collect(Collectors.joining());
    }
}
