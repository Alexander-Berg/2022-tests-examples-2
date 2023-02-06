package ru.yandex.metrika.mobmet.intapi.common;

import java.util.List;
import java.util.Random;

import org.apache.commons.math3.random.RandomDataGenerator;

import ru.yandex.metrika.common.test.medium.RandomUtils;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.AppLabel;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.CampaignPlatform;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;
import ru.yandex.metrika.segments.apps.misc.FingerprintAttributionWindow;
import ru.yandex.metrika.segments.apps.misc.MobPlatform;
import ru.yandex.metrika.segments.apps.misc.PartnerType;
import ru.yandex.metrika.segments.apps.misc.StrictAttributionWindow;

public class TestData {

    public static final int FOOD_APP_CATEGORY = 91;

    private TestData() {

    }

    public static long randomUid() {
        return new RandomDataGenerator().nextLong(1, 1000000000);
    }

    public static String randomString() {
        return RandomUtils.getRandomString(new Random(0), 20);
    }

    public static Application defaultApp() {
        return Application.builder()
                .setName("test")
                .setCategory(FOOD_APP_CATEGORY)
                .build();
    }

    public static Campaign defaultCampaign(long trackingId, int appId, long partnerId, long targetUrlId) {
        Campaign campaign = new Campaign();
        campaign.setTrackingId(Long.toString(trackingId));
        campaign.setName("campaign_" + randomString());
        campaign.setApiKey(appId);
        campaign.setPartnerId(partnerId);
        campaign.setPlatforms(List.of(defaultPlatform(targetUrlId)));
        campaign.setStrictAttributionWindow(StrictAttributionWindow.nine_days);
        campaign.setFingerprintAttributionWindow(FingerprintAttributionWindow.twelve_hours);
        campaign.setPostbacks(List.of());
        campaign.setReattributionEnabled(false);
        return campaign;
    }

    public static CampaignPlatform defaultPlatform(long targetUrlId) {
        CampaignPlatform platform = new CampaignPlatform();
        platform.setTargetUrlId(targetUrlId);
        platform.setName(MobPlatform.android);
        return platform;
    }

    public static AppTargetUrl defaultTargetUrl() {
        AppTargetUrl targetUrl = new AppTargetUrl();
        targetUrl.setPlatform(MobPlatform.android);
        targetUrl.setUrl("targetUrlUrl" + randomString());
        targetUrl.setTitle("targetUrlTitle" + randomString());
        return targetUrl;
    }

    public static TrackingPartner defaultPartner(long uid) {
        TrackingPartner partner = new TrackingPartner();
        partner.setName("partner_" + randomString());
        partner.setType(PartnerType.ORDINARY);
        partner.setUid(uid);
        partner.setWebsiteUrl("https://website.com");
        return partner;
    }

    public static AppLabel defaultLabel(long uid) {
        AppLabel label = new AppLabel();
        label.setName("label_" + randomString());
        label.setUid(uid);
        return label;
    }
}
