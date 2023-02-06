package ru.yandex.metrika.mobmet.dao.redirect;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.CampaignPlatform;
import ru.yandex.metrika.mobmet.model.redirect.Postback;
import ru.yandex.metrika.mobmet.model.redirect.PostbackHeader;
import ru.yandex.metrika.segments.apps.misc.FingerprintAttributionWindow;
import ru.yandex.metrika.segments.apps.misc.MobPlatform;
import ru.yandex.metrika.segments.apps.misc.PartnerType;
import ru.yandex.metrika.segments.apps.misc.PartnerTypes;
import ru.yandex.metrika.segments.apps.misc.StrictAttributionWindow;
import ru.yandex.metrika.spring.TranslationHelper;

import static org.mockito.Matchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.ADWORDS_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.DIRECT_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.DOUBLECLICK_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.FACEBOOK_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.HUAWEI_ADS_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.MYTARGET_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.ORDINARY_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.SEARCH_ADS_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.TIKTOK_PARTNER_ID;

public class TrackerProcessorTest {

    private static final List<PostbackHeader> DIRECT_HEADER = List.of(new PostbackHeader("pass-phrase", "stubForTest"));
    private static final List<PostbackHeader> TIKTOK_HEADER = List.of(new PostbackHeader("Authorization", "stubForTest"));

    private static final String TRACKING_ID = "0000";
    private static final int API_KEY = 2;

    private final MultiplatformDao multiplatformDao = mock(MultiplatformDao.class);
    private final PartnerTypes partnerTypes = mock(PartnerTypes.class);

    private static final TrackingErrorsMessageGenerator messageGenerator =
            new TrackingErrorsMessageGenerator(new TranslationHelperStub());

    private final EmptyPlatformsFieldsProcessor emptyPlatformsFieldsProcessor = new EmptyPlatformsFieldsProcessor(multiplatformDao);
    private final CommonProcessor processor = new CommonProcessor(
            partnerTypes,
            ImmutableMap.of(PartnerType.DOUBLECLICK, emptyPlatformsFieldsProcessor,
                    PartnerType.ADWORDS, new AdwordsFieldsProcessor(new AdwordsSettings(), emptyPlatformsFieldsProcessor),
                    PartnerType.DIRECT, new DirectFieldsProcessor(new DirectSettings()),
                    PartnerType.TIKTOK, new TiktokFieldsProcessor(messageGenerator, new TiktokSettings())));

    private final List<CampaignPlatform> emptyPlatforms = ImmutableList.of(
            new CampaignPlatform().withName(MobPlatform.android),
            new CampaignPlatform().withName(MobPlatform.iOS));

    private final List<CampaignPlatform> dbEmptyPlatforms = ImmutableList.of(
            new CampaignPlatform().withName(MobPlatform.android).withId(0L).withTrackingId(TRACKING_ID),
            new CampaignPlatform().withName(MobPlatform.iOS).withId(1L).withTrackingId(TRACKING_ID));

    private final List<CampaignPlatform> singlePlatforms = Collections.singletonList(
            new CampaignPlatform().withName(MobPlatform.android).withId(0L).withTrackingId(TRACKING_ID));

    @Before
    public void setup() {
        when(partnerTypes.determineTypeForPartner(ORDINARY_PARTNER_ID)).thenReturn(PartnerType.ORDINARY);
        when(partnerTypes.determineTypeForPartner(FACEBOOK_PARTNER_ID)).thenReturn(PartnerType.FACEBOOK);
        when(partnerTypes.determineTypeForPartner(DIRECT_PARTNER_ID)).thenReturn(PartnerType.DIRECT);
        when(partnerTypes.determineTypeForPartner(MYTARGET_PARTNER_ID)).thenReturn(PartnerType.MYTARGET);
        when(partnerTypes.determineTypeForPartner(ADWORDS_PARTNER_ID)).thenReturn(PartnerType.ADWORDS);
        when(partnerTypes.determineTypeForPartner(SEARCH_ADS_PARTNER_ID)).thenReturn(PartnerType.SEARCH_ADS);
        when(partnerTypes.determineTypeForPartner(DOUBLECLICK_PARTNER_ID)).thenReturn(PartnerType.DOUBLECLICK);
        when(partnerTypes.determineTypeForPartner(TIKTOK_PARTNER_ID)).thenReturn(PartnerType.TIKTOK);
        when(partnerTypes.determineTypeForPartner(HUAWEI_ADS_PARTNER_ID)).thenReturn(PartnerType.HUAWEI_ADS);
    }

    @Test
    public void adwordsPlatformsRead() {
        Campaign campaign = createOrdinaryAndroidCampaignWithoutPlatforms();
        campaign.setPartnerId(ADWORDS_PARTNER_ID);
        campaign.setPlatforms(dbEmptyPlatforms);
        processor.postprocess(campaign);
        Assert.assertTrue(campaign.getPlatforms().isEmpty());
    }

    @Test
    public void adwordsNewPlatformsWrite() {
        when(multiplatformDao.select(any())).thenReturn(new ArrayList<>());
        Campaign campaign = createOrdinaryAndroidCampaignWithoutPlatforms();
        campaign.setPartnerId(ADWORDS_PARTNER_ID);
        processor.preprocess(campaign);
        Assert.assertEquals(emptyPlatforms, campaign.getPlatforms());
    }

    @Test
    public void adwordsExistedPlatformsWrite() {
        when(multiplatformDao.select(any())).thenReturn(dbEmptyPlatforms);
        Campaign campaign = createOrdinaryAndroidCampaignWithoutPlatforms();
        campaign.setPartnerId(ADWORDS_PARTNER_ID);
        processor.preprocess(campaign);
        Assert.assertEquals(dbEmptyPlatforms, campaign.getPlatforms());
    }

    @Test
    public void doubleClickPlatformsRead() {
        Campaign campaign = createOrdinaryAndroidCampaignWithoutPlatforms();
        campaign.setPartnerId(DOUBLECLICK_PARTNER_ID);
        campaign.setPlatforms(dbEmptyPlatforms);
        processor.postprocess(campaign);
        Assert.assertTrue(campaign.getPlatforms().isEmpty());
    }

    @Test
    public void doubleClickNewPlatformsWrite() {
        when(multiplatformDao.select(any())).thenReturn(new ArrayList<>());
        Campaign campaign = createOrdinaryAndroidCampaignWithoutPlatforms();
        campaign.setPartnerId(DOUBLECLICK_PARTNER_ID);
        processor.preprocess(campaign);
        Assert.assertEquals(emptyPlatforms, campaign.getPlatforms());
    }

    @Test
    public void doubleClickExistedPlatformsWrite() {
        when(multiplatformDao.select(any())).thenReturn(dbEmptyPlatforms);
        Campaign campaign = createOrdinaryAndroidCampaignWithoutPlatforms();
        campaign.setPartnerId(DOUBLECLICK_PARTNER_ID);
        processor.preprocess(campaign);
        Assert.assertEquals(dbEmptyPlatforms, campaign.getPlatforms());
    }

    @Test
    public void adwordsLegacyPlatformsRead() {
        Campaign campaign = createOrdinaryAndroidCampaignWithoutPlatforms();
        campaign.setPartnerId(ADWORDS_PARTNER_ID);
        campaign.setPlatforms(singlePlatforms);
        processor.postprocess(campaign);
        Assert.assertEquals(singlePlatforms, campaign.getPlatforms());
    }

    @Test
    public void adwordsLegacyPlatformsWrite() {
        when(multiplatformDao.select(any())).thenReturn(singlePlatforms);
        Campaign campaign = createOrdinaryAndroidCampaignWithoutPlatforms();
        campaign.setPartnerId(ADWORDS_PARTNER_ID);
        processor.preprocess(campaign);
        Assert.assertEquals(singlePlatforms, campaign.getPlatforms());
    }

    @Test
    public void adwordsPostbackRead() {
        when(multiplatformDao.select(any())).thenReturn(dbEmptyPlatforms);
        Campaign campaign = createOrdinaryAndroidCampaignWithoutPlatforms();
        campaign.setPartnerId(ADWORDS_PARTNER_ID);
        List<Postback> input = ImmutableList.of(
                new Postback(1L, "https/url.ru"),
                new Postback(2L, "https://www.googleadservices.com/pagead/conversion/app/?user_params=2&dev_token=324234")
        );
        campaign.setPostbacks(input);
        processor.postprocess(campaign);
        List<Postback> expected = ImmutableList.of(
                new Postback(1L, "https/url.ru"),
                new Postback(2L, "https://www.googleadservices.com/pagead/conversion/app/?user_params=2")
        );
        Assert.assertEquals(expected, campaign.getPostbacks());
    }

    @Test
    public void adwordsPostbackWrite() {
        when(multiplatformDao.select(any())).thenReturn(dbEmptyPlatforms);
        Campaign campaign = createOrdinaryAndroidCampaignWithoutPlatforms();
        campaign.setPartnerId(ADWORDS_PARTNER_ID);
        List<Postback> input = ImmutableList.of(
                new Postback(1L, "https/url.ru"),
                new Postback(2L, "https://www.googleadservices.com/pagead/conversion/app/?user_params=2")
        );
        campaign.setPostbacks(input);
        processor.preprocess(campaign);
        List<Postback> expected = ImmutableList.of(
                new Postback(1L, "https/url.ru"),
                new Postback(2L, "https://www.googleadservices.com/pagead/conversion/app/?user_params=2&dev_token=stubForTest")
        );
        Assert.assertEquals(expected, campaign.getPostbacks());
    }

    @Test
    public void directPostbackHeadersRead() {
        when(multiplatformDao.select(any())).thenReturn(singlePlatforms);
        Campaign campaign = createCommonAndroidCampaign(DIRECT_PARTNER_ID);
        List<Postback> input = ImmutableList.of(
                new Postback(1L, "https/url.ru"),
                new Postback(2L, "https://yabs.yandex.ru/test").withHeaders(DIRECT_HEADER),
                new Postback(3L, "http://yabs.yandex.ru/test1").withHeaders(DIRECT_HEADER)
        );
        campaign.setPostbacks(input);
        processor.postprocess(campaign);
        List<Postback> expected = ImmutableList.of(
                new Postback(1L, "https/url.ru"),
                new Postback(2L, "https://yabs.yandex.ru/test"),
                new Postback(3L, "http://yabs.yandex.ru/test1")
        );
        Assert.assertEquals(expected, campaign.getPostbacks());
    }

    @Test
    public void directPostbackHeadersWrite() {
        when(multiplatformDao.select(any())).thenReturn(singlePlatforms);
        Campaign campaign = createCommonAndroidCampaign(DIRECT_PARTNER_ID);
        List<Postback> input = ImmutableList.of(
                new Postback(1L, "https/url.ru"),
                new Postback(2L, "http://yabs.yandex.ru/test1"),
                new Postback(3L, "https://yabs.yandex.ru/test")
        );
        campaign.setPostbacks(input);
        processor.preprocess(campaign);
        List<Postback> expected = ImmutableList.of(
                new Postback(1L, "https/url.ru"),
                new Postback(2L, "http://yabs.yandex.ru/test1").withHeaders(DIRECT_HEADER),
                new Postback(3L, "https://yabs.yandex.ru/test").withHeaders(DIRECT_HEADER)
        );
        Assert.assertEquals(expected, campaign.getPostbacks());
    }

    @Test
    public void tiktokPreprocess() {
        when(multiplatformDao.select(any())).thenReturn(new ArrayList<>());
        Campaign campaign = createCommonAndroidCampaign(TIKTOK_PARTNER_ID);
        campaign.setTiktokAppId("12345");
        List<Postback> input = ImmutableList.of(
                new Postback(1L, "https://analytics.tiktok.com/api/v1/track", """
                        {"context":{"app":{}}}""")
        );
        campaign.setPostbacks(input);
        processor.preprocess(campaign);
        List<Postback> expected = ImmutableList.of(
                new Postback(1L, "https://analytics.tiktok.com/api/v1/track", """
                        {"context":{"app":{"tiktok_app_id":"12345"}}}""")
                        .withHeaders(TIKTOK_HEADER)
        );
        Assert.assertEquals(expected, campaign.getPostbacks());
    }

    @Test
    public void tiktokPostprocess() {
        when(multiplatformDao.select(any())).thenReturn(new ArrayList<>());
        Campaign campaign = createCommonAndroidCampaign(TIKTOK_PARTNER_ID);
        campaign.setTiktokAppId("12345");
        List<Postback> input = ImmutableList.of(
                new Postback(1L, "https://analytics.tiktok.com/api/v1/track", """
                        {"context":{"app":{"tiktok_app_id":"12345"}}}""")
                        .withHeaders(TIKTOK_HEADER)
        );
        campaign.setPostbacks(input);
        processor.postprocess(campaign);
        List<Postback> expected = ImmutableList.of(
                new Postback(1L, "https://analytics.tiktok.com/api/v1/track", """
                        {"context":{"app":{"tiktok_app_id":"12345"}}}""")
        );
        Assert.assertEquals(expected, campaign.getPostbacks());
    }

    private static Campaign createOrdinaryAndroidCampaignWithoutPlatforms() {
        Campaign campaign = createCommonAndroidCampaign(ORDINARY_PARTNER_ID);
        campaign.setStrictAttributionWindow(StrictAttributionWindow.ten_days);
        return campaign;
    }

    private static Campaign createCommonAndroidCampaign(long partnerId) {
        Campaign campaign = createCommonCampaign();
        campaign.setPartnerId(partnerId);
        return campaign;
    }

    private static Campaign createCommonCampaign() {
        Campaign campaign = new Campaign();
        campaign.setName("Name");
        campaign.setApiKey(API_KEY);
        campaign.setTrackingId(TRACKING_ID);
        campaign.setStrictAttributionWindow(StrictAttributionWindow.nine_days);
        campaign.setFingerprintAttributionWindow(FingerprintAttributionWindow.one_day);
        campaign.setPostbacks(Collections.emptyList());
        return campaign;
    }

    private static class TranslationHelperStub extends TranslationHelper {
        @Override
        public String localizeMessage(String message, Object... args) {
            return message;
        }
    }
}
