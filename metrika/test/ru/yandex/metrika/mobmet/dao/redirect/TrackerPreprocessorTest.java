package ru.yandex.metrika.mobmet.dao.redirect;


import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

import com.google.common.collect.ImmutableMap;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.hamcrest.TypeSafeMatcher;
import org.jetbrains.annotations.NotNull;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;

import ru.yandex.metrika.api.error.ConflictApiException;
import ru.yandex.metrika.api.error.LimitException;
import ru.yandex.metrika.mobmet.model.redirect.AdwordsConversion;
import ru.yandex.metrika.mobmet.model.redirect.AppDeepLink;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.CampaignPlatform;
import ru.yandex.metrika.mobmet.model.redirect.Postback;
import ru.yandex.metrika.mobmet.model.redirect.PostbackKind;
import ru.yandex.metrika.mobmet.model.redirect.PostbackMethod;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;
import ru.yandex.metrika.segments.apps.misc.FingerprintAttributionWindow;
import ru.yandex.metrika.segments.apps.misc.MobPlatform;
import ru.yandex.metrika.segments.apps.misc.PartnerType;
import ru.yandex.metrika.segments.apps.misc.PartnerTypes;
import ru.yandex.metrika.segments.apps.misc.PostbackAttributionWindow;
import ru.yandex.metrika.segments.apps.misc.StrictAttributionWindow;
import ru.yandex.metrika.spring.TranslationHelper;

import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.ADWORDS_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.DIRECT_AUTO_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.DOUBLECLICK_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.FACEBOOK_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.HUAWEI_ADS_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.MYTARGET_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.ORDINARY_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.SEARCH_ADS_PARTNER_ID;
import static ru.yandex.metrika.mobmet.dao.redirect.PartnerIds.TIKTOK_PARTNER_ID;
import static ru.yandex.metrika.segments.apps.misc.FingerprintAttributionWindow.none;
import static ru.yandex.metrika.segments.apps.misc.FingerprintAttributionWindow.one_hour;

public class TrackerPreprocessorTest {

    private static final String TRACKING_ID = "0000";
    private static final int API_KEY = 2;
    private static final long DEEP_LINK_ID = 1L;
    private static final long TARGET_URL_ID = 2L;

    private final CampaignsDao campaignsDao = mock(CampaignsDao.class);
    private final DeepLinkDao deepLinkDao = mock(DeepLinkDao.class);
    private final TargetUrlDao targetUrlDao = mock(TargetUrlDao.class);
    private final PartnerTypes partnerTypes = mock(PartnerTypes.class);

    private static final TrackingErrorsMessageGenerator messageGenerator =
            new TrackingErrorsMessageGenerator(new TranslationHelperStub());

    private final Map<PartnerType, SpecificFieldsCheck> checks = ImmutableMap.<PartnerType, SpecificFieldsCheck>builder()
            .put(PartnerType.DOUBLECLICK, new DoubleClickFieldsCheck(messageGenerator))
            .put(PartnerType.ADWORDS, new AdwordsFieldsCheck(messageGenerator, campaignsDao))
            .put(PartnerType.FACEBOOK, new FacebookFieldsCheck(messageGenerator, campaignsDao))
            .put(PartnerType.HUAWEI_ADS, new HuaweiAdsFieldsCheck(messageGenerator, campaignsDao))
            .build();

    private final TrackerPreprocessor preprocessor = new TrackerPreprocessor(campaignsDao, deepLinkDao, targetUrlDao, partnerTypes,
            messageGenerator, checks);

    @Rule
    public ExpectedException expectedException = ExpectedException.none();

    @Before
    public void before() {
        when(campaignsDao.select(anyString(), anyInt())).thenReturn(Optional.empty());

        when(partnerTypes.determineTypeForPartner(ORDINARY_PARTNER_ID)).thenReturn(PartnerType.ORDINARY);
        when(partnerTypes.determineTypeForPartner(FACEBOOK_PARTNER_ID)).thenReturn(PartnerType.FACEBOOK);
        when(partnerTypes.determineTypeForPartner(MYTARGET_PARTNER_ID)).thenReturn(PartnerType.MYTARGET);
        when(partnerTypes.determineTypeForPartner(ADWORDS_PARTNER_ID)).thenReturn(PartnerType.ADWORDS);
        when(partnerTypes.determineTypeForPartner(SEARCH_ADS_PARTNER_ID)).thenReturn(PartnerType.SEARCH_ADS);
        when(partnerTypes.determineTypeForPartner(DOUBLECLICK_PARTNER_ID)).thenReturn(PartnerType.DOUBLECLICK);
        when(partnerTypes.determineTypeForPartner(DIRECT_AUTO_PARTNER_ID)).thenReturn(PartnerType.DIRECT_AUTO);
        when(partnerTypes.determineTypeForPartner(TIKTOK_PARTNER_ID)).thenReturn(PartnerType.TIKTOK);
        when(partnerTypes.determineTypeForPartner(HUAWEI_ADS_PARTNER_ID)).thenReturn(PartnerType.HUAWEI_ADS);

        final AppDeepLink deepLink = new AppDeepLink();
        deepLink.setPlatform(MobPlatform.android);
        when(deepLinkDao.selectOne(API_KEY, DEEP_LINK_ID)).thenReturn(deepLink);

        final AppTargetUrl targetUrl = new AppTargetUrl();
        targetUrl.setPlatform(MobPlatform.android);
        when(targetUrlDao.selectOne(API_KEY, TARGET_URL_ID)).thenReturn(targetUrl);
    }

    @Test
    public void testTooManyPostbacks() {
        Campaign campaign = createOrdinaryAndroidCampaign();
        Postback postback = new Postback(1L, "http://test.ru", PostbackMethod.GET, List.of(),
                null, PostbackKind.cpa, "event", null, null, false, PostbackAttributionWindow.eight_days, true, false, null);
        List<Postback> postbacks = new ArrayList<>();
        for (int i = 0; i < 11; ++i) {
            postbacks.add(postback);
        }
        campaign.setPostbacks(postbacks);
        expectedException.expect(LimitException.class);
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testFacebookPositive() {
        Campaign campaign = createFacebookAndroidCampaign();
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testFacebookNegativeHasTargetId() {
        Campaign campaign = createFacebookAndroidCampaign();
        campaign.getPlatforms().get(0).setTargetUrlId(TARGET_URL_ID);

        expectedException.expect(createConflictApiExceptionMatcher("target_url", "target_url forbidden"));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testFacebookNegativeManyPlatforms() {
        Campaign campaign = createFacebookAndroidCampaign();

        CampaignPlatform androidPlatform = new CampaignPlatform();
        androidPlatform.setDeepLinkId(DEEP_LINK_ID);
        androidPlatform.setTargetUrlId(TARGET_URL_ID);
        androidPlatform.setName(MobPlatform.android);

        CampaignPlatform iosPlatform = new CampaignPlatform();
        iosPlatform.setDeepLinkId(DEEP_LINK_ID);
        iosPlatform.setTargetUrlId(TARGET_URL_ID);
        iosPlatform.setName(MobPlatform.iOS);

        campaign.setPlatforms(Arrays.asList(androidPlatform, iosPlatform));

        expectedException.expect(ConflictApiException.class);
        expectedException.expectMessage("Wrong platforms count for facebook partner");
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testFacebookDuplicateDecryptionKey() {
        Campaign campaign = createFacebookAndroidCampaign().setFacebookDecryptionKey("abacaba");
        when(campaignsDao.findFacebookDecryptionKeyConflict(campaign))
                .thenReturn(Optional.of("1234"));

        expectedException.expect(createConflictApiExceptionMatcher(
                "facebook_decryption_key", messageGenerator.facebookDecryptionKeyConflict(API_KEY, "1234")));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testHuaweiDuplicateLinkId() {
        String conflictTrackingId = "1234";
        Campaign campaign = createHuaweiAdsCampaign().setHuaweiLinkId("abacaba");
        when(campaignsDao.findHuaweiLinkIdConflict(campaign))
                .thenReturn(Optional.of(conflictTrackingId));

        expectedException.expect(createConflictApiExceptionMatcher(
                "huawei_link_id", messageGenerator.huaweiLinkIdConflict(API_KEY, conflictTrackingId)));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testMyTargetPositive() {
        Campaign campaign = createMyTargetAndroidCampaign();
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testMyTargetTargetUrlRequired() {
        Campaign campaign = createMyTargetAndroidCampaign();
        campaign.getPlatforms().get(0).setTargetUrlId(null);

        expectedException.expect(createConflictApiExceptionMatcher(null, "Целевая ссылка не может быть пустой."));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testMyTargetPostclickUrlForbidden() {
        Campaign campaign = createMyTargetAndroidCampaign();
        campaign.getPlatforms().get(0).setPostClickUrl("test");

        expectedException.expect(createConflictApiExceptionMatcher("platform", "Postclick url should be empty"));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testAdwordsPositive() {
        Campaign campaign = createAdwordsAndroidCampaign();
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testAdwordsRequiredTargetUrlOnIos() {
        Campaign campaign = createAdwordsAndroidCampaign();
        campaign.setAdwordsLinkId(null);
        CampaignPlatform iosPlatform = new CampaignPlatform();
        iosPlatform.setName(MobPlatform.iOS);
        campaign.setPlatforms(singletonList(iosPlatform));

        expectedException.expect(createConflictApiExceptionMatcher(null, "Целевая ссылка не может быть пустой."));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testAdwordsLinkIDNonRequiredPlatformOrTargetUrlPositive() {
        Campaign campaign = createAdwordsAndroidCampaign();
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testConversionIdForOrdinaryTracker() {
        final Campaign campaign = createOrdinaryAndroidCampaign();
        campaign.setAdwordsConversionId("Not empty ConversionID");
        expectedException.expect(ConflictApiException.class);
        expectedException.expectMessage("Партнер не поддерживает идентификатор связи, " +
                "идентификатор конверсии и ярлык конверсии. Пожалуйста, не указывайте эти значения.");
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testConversionLabelForOrdinaryTracker() {
        final Campaign campaign = createOrdinaryAndroidCampaign();
        campaign.setAdwordsConversionLabel("Not empty ConversionID");
        expectedException.expect(ConflictApiException.class);
        expectedException.expectMessage("Партнер не поддерживает идентификатор связи, " +
                "идентификатор конверсии и ярлык конверсии. Пожалуйста, не указывайте эти значения.");
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testAdwordsDuplicateConversionOldPair() {
        Campaign campaign = createAdwordsAndroidCampaign().setAdwordsLinkId(null);

        expectedException.expect(createConflictApiExceptionMatcher(null, messageGenerator.duplicatedConversionInfo(API_KEY, "1115", false)));

        Campaign duplicateConversionCampaign = createAdwordsAndroidCampaign().setAdwordsLinkId(null);
        duplicateConversionCampaign.setTrackingId("1115");
        AdwordsConversion duplicateAdwordsConversion = AdwordsConversion.createForCampaign(API_KEY, duplicateConversionCampaign);

        when(campaignsDao.findGoogleAdsConflict(campaign))
                .thenReturn(Optional.of(duplicateAdwordsConversion));

        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testAdwordsDuplicateConversionLinkID() {
        Campaign campaign = createAdwordsAndroidCampaign();
        campaign.setAdwordsConversionId(null);
        campaign.setAdwordsConversionLabel(null);

        expectedException.expect(createConflictApiExceptionMatcher(null, messageGenerator.duplicatedConversionInfo(API_KEY, "1116", true)));

        Campaign duplicateConversionCampaign = createAdwordsAndroidCampaign();
        duplicateConversionCampaign.setAdwordsConversionId(null);
        duplicateConversionCampaign.setAdwordsConversionLabel(null);
        duplicateConversionCampaign.setTrackingId("1116");
        AdwordsConversion duplicateAdwordsConversion = AdwordsConversion.createForCampaign(API_KEY, duplicateConversionCampaign);

        when(campaignsDao.findGoogleAdsConflict(campaign))
                .thenReturn(Optional.of(duplicateAdwordsConversion));

        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testAdwordsConversionIdMissing() {
        Campaign campaign = createAdwordsAndroidCampaign();
        campaign.setAdwordsConversionId(null);

        expectedException.expect(createConflictApiExceptionMatcher(null, "Идентификатор конверсии не должен быть пустым."));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testAdwordsConversionLabelMissing() {
        Campaign campaign = createAdwordsAndroidCampaign();
        campaign.setAdwordsConversionLabel(null);

        expectedException.expect(createConflictApiExceptionMatcher(null, "Ярлык конверсии не может быть пустым."));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testAdwordsLinkIdMissingWithOldPairBeingSpecified() {
        Campaign campaign = createAdwordsAndroidCampaign();
        campaign.setAdwordsLinkId(null);
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testAdwordsOldPairMissingWithLinkIdBeingSpeicified() {
        Campaign campaign = createAdwordsAndroidCampaign();
        campaign.setAdwordsConversionId(null);
        campaign.setAdwordsConversionLabel(null);
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testAdwordsAllConversionInfoMissing() {
        Campaign campaign = createAdwordsAndroidCampaign();
        campaign.setAdwordsLinkId(null);
        campaign.setAdwordsConversionId(null);
        campaign.setAdwordsConversionLabel(null);

        expectedException.expect(createConflictApiExceptionMatcher(null, "Идентификатор связи не может быть пустым."));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testAdwordsConversionIdMissingWithLinkIdBeingSpecified() {
        Campaign campaign = createAdwordsAndroidCampaign();
        campaign.setAdwordsConversionId(null);

        expectedException.expect(createConflictApiExceptionMatcher(null, "Идентификатор конверсии не должен быть пустым."));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testAdwordsConversionLabelMissingWithLinkIdBeingSpecified() {
        Campaign campaign = createAdwordsAndroidCampaign();
        campaign.setAdwordsConversionLabel(null);

        expectedException.expect(createConflictApiExceptionMatcher(null, "Ярлык конверсии не может быть пустым."));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testSearchAdsUpdate() {
        Campaign campaign = createSearchAdsCampaign();
        preprocessor.prepareBeforeUpdate(campaign);
    }

    @Test
    public void testSearchAdsDeeplinkForbidden() {
        Campaign campaign = createSearchAdsCampaign();
        campaign.getPlatforms().get(0).setDeepLinkId(SEARCH_ADS_PARTNER_ID);

        expectedException.expect(createConflictApiExceptionMatcher("deep_link", "Deep link forbidden"));
        preprocessor.prepareBeforeUpdate(campaign);
    }

    @Test
    public void testSearchAdsCreationForbidden() {
        Campaign campaign = createSearchAdsCampaign();
        expectedException.expect(createConflictApiExceptionMatcher(null, "Creation of search_ads tracker is forbidden"));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testDirectAutoCreationForbidden() {
        Campaign campaign = createDirectAutoCampaign();
        expectedException.expect(createConflictApiExceptionMatcher(null, "Creation of direct_auto tracker is forbidden"));
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testDirectAutoUpdateForbidden() {
        Campaign campaign = createDirectAutoCampaign();
        expectedException.expect(createConflictApiExceptionMatcher(null, "Update of direct_auto tracker is forbidden"));
        preprocessor.prepareBeforeUpdate(campaign);
    }

    @Test
    public void testDoubleClickCreation() {
        final Campaign campaing = createDoubleClickCampaign();
        preprocessor.prepareBeforeCreate(campaing);
    }

    @Test
    public void testDoubleClickPlatformAbsence() {
        final Campaign campaign = createDoubleClickCampaignWithPlatform();
        expectedException.expect(ConflictApiException.class);
        expectedException.expectMessage("Wrong platforms count for doubleclick partner");
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testDoubleClickFawFailing() {
        final Campaign campaign = createDoubleClickCampaignWithFaw();
        expectedException.expect(ConflictApiException.class);
        expectedException.expectMessage("Not supported fingerprint attribution window");
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testDoubleClickRequiredSrc() {
        final Campaign campaign = createDoubleClickCampaignWithEmptySrc();
        expectedException.expect(ConflictApiException.class);
        expectedException.expectMessage("Поле src не может быть пустым");
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testDoubleClickRequiredCat() {
        final Campaign campaign = createDoubleClickCampaignWithEmptyCat();
        expectedException.expect(ConflictApiException.class);
        expectedException.expectMessage("Поле cat не может быть пустым");
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testDoubleClickRequiredType() {
        final Campaign campaign = createDoubleClickCampaignWithEmptyType();
        expectedException.expect(ConflictApiException.class);
        expectedException.expectMessage("Поле type не может быть пустым");
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testDoubleClickRequiredToken() {
        final Campaign campaign = createDoubleClickCampaignWithToken();
        expectedException.expect(ConflictApiException.class);
        expectedException.expectMessage("Поле authorization token не может быть пустым");
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testCatTypeForOrdinaryTracker() {
        final Campaign campaign = createCommonAndroidCampaign(ORDINARY_PARTNER_ID);
        campaign.setDoubleClickCat("Not empty cat");
        expectedException.expect(ConflictApiException.class);
        expectedException.expectMessage("Поле cat может быть задано только для партнера DoubleClick");
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testRemarketingCampaign() {
        final Campaign campaign = createRemarketingCampaign();
        preprocessor.prepareBeforeCreate(campaign);
    }

    @Test
    public void testCpaPostbackClientNotEmptyEventSubtype() {
        testCpaPostback(null, AppEventType.EVENT_CLIENT, "order",
                "'event_name' must be not empty and 'event_subtype' must be null for client event");
    }

    @Test
    public void testCpaPostbackClientEmptyEventName() {
        testCpaPostback(null, AppEventType.EVENT_CLIENT, null,
                "'event_name' must be not empty and 'event_subtype' must be null for client event");
    }

    @Test
    public void testCpaPostbackClientNotEmptyEventNameAndSubtype() {
        testCpaPostback("not empty!", AppEventType.EVENT_CLIENT, "order",
                "'event_name' must be not empty and 'event_subtype' must be null for client event");
    }

    @Test
    public void testCpaPostbackEcommerceNotEmptyEventName() {
        testCpaPostback("not empty!", AppEventType.ECOMMERCE, null,
                "'event_name' must be null and 'event_subtype' must be not empty for ecommerce event");
    }

    @Test
    public void testCpaPostbackEcommerceEmptyEventSubtype() {
        testCpaPostback(null, AppEventType.ECOMMERCE, null,
                "'event_name' must be null and 'event_subtype' must be not empty for ecommerce event");
    }

    @Test
    public void testCpaPostbackEcommerceNotEmptyEventNameAndSubtype() {
        testCpaPostback("not empty!", AppEventType.ECOMMERCE, "order",
                "'event_name' must be null and 'event_subtype' must be not empty for ecommerce event");
    }

    @Test
    public void testCpaPostbackEcommerceIllegalSubtype() {
        testCpaPostback(null, AppEventType.ECOMMERCE, "preorder",
                "Illegal event subtype preorder");
    }

    @Test
    public void testCpiPostbackNonEmptyEventNameFails() {
        testNonCpaPostbackNonEmptyEventFails(PostbackKind.cpi, "not-empty!", null, null);
    }

    @Test
    public void testCprPostbackNonEmptyEventNameFails() {
        testNonCpaPostbackNonEmptyEventFails(PostbackKind.cpr, "not-empty!", null, null);
    }

    @Test
    public void testCpiPostbackNonEmptyEventSubtypeFails() {
        testNonCpaPostbackNonEmptyEventFails(PostbackKind.cpi, null, AppEventType.ECOMMERCE, "order");
    }

    @Test
    public void testCprPostbackNonEmptyEventSubtypeFails() {
        testNonCpaPostbackNonEmptyEventFails(PostbackKind.cpr, null, AppEventType.ECOMMERCE, "order");
    }

    private void testNonCpaPostbackNonEmptyEventFails(PostbackKind postbackKind,
                                                      String eventName,
                                                      AppEventType eventType,
                                                      String eventSubtype) {
        final Campaign campaign = createOrdinaryAndroidCampaign();
        campaign.setPostbacks(singletonList(new Postback(1L, "http://test.ru", PostbackMethod.GET, null, null,
                postbackKind, eventName, eventType, eventSubtype, false, PostbackAttributionWindow.eight_days, true, false, null)));
        expectedException.expect(ConflictApiException.class);
        expectedException.expectMessage("'event_name' and 'event_subtype' fields are allowed for cpa postbacks only");
        preprocessor.prepareBeforeCreate(campaign);
    }

    private void testCpaPostback(String eventName, AppEventType eventType, String eventSubtype, String errorMessage) {
        Campaign campaign = createOrdinaryAndroidCampaign();
        campaign.setPostbacks(singletonList(new Postback(1L, "http://test.ru", PostbackMethod.GET, List.of(), null,
                PostbackKind.cpa, eventName, eventType, eventSubtype,
                false, PostbackAttributionWindow.eight_days, true, false, null)));
        expectedException.expect(ConflictApiException.class);
        expectedException.expectMessage(errorMessage);
        preprocessor.prepareBeforeCreate(campaign);
    }

    private static Campaign createDoubleClickCampaign() {
        final Campaign campaign = createCommonCampaign(DOUBLECLICK_PARTNER_ID);
        campaign.setFingerprintAttributionWindow(none);
        campaign.setDoubleClickSrc("Src");
        campaign.setDoubleClickCat("Cat");
        campaign.setDoubleClickType("Type");
        campaign.setDoubleClickToken("Token");
        return campaign;
    }

    private static Campaign createDoubleClickCampaignWithPlatform() {
        final Campaign campaign = createDoubleClickCampaign();
        campaign.setPlatforms(singletonList(androidPlatform()));
        return campaign;
    }

    private static Campaign createDoubleClickCampaignWithFaw() {
        final Campaign campaign = createDoubleClickCampaign();
        campaign.setFingerprintAttributionWindow(one_hour);
        return campaign;
    }

    private static Campaign createDoubleClickCampaignWithEmptySrc() {
        final Campaign campaign = createDoubleClickCampaign();
        campaign.setDoubleClickSrc(null);
        return campaign;
    }

    private static Campaign createDoubleClickCampaignWithEmptyCat() {
        final Campaign campaign = createDoubleClickCampaign();
        campaign.setDoubleClickCat("");
        return campaign;
    }

    private static Campaign createDoubleClickCampaignWithEmptyType() {
        final Campaign campaign = createDoubleClickCampaign();
        campaign.setDoubleClickType("    ");
        return campaign;
    }

    private static Campaign createDoubleClickCampaignWithToken() {
        final Campaign campaign = createDoubleClickCampaign();
        campaign.setDoubleClickToken("\n");
        return campaign;
    }

    private static Campaign createFacebookAndroidCampaign() {
        return createCommonAndroidCampaign(FACEBOOK_PARTNER_ID);
    }

    private static Campaign createHuaweiAdsCampaign() {
        return createCommonAndroidCampaign(HUAWEI_ADS_PARTNER_ID);
    }

    private static Campaign createMyTargetAndroidCampaign() {
        Campaign campaign = createCommonAndroidCampaign(MYTARGET_PARTNER_ID);
        campaign.getPlatforms().get(0).setTargetUrlId(TARGET_URL_ID);
        return campaign;
    }

    private static Campaign createSearchAdsCampaign() {
        Campaign campaign = createCommonCampaign();
        campaign.setPartnerId(SEARCH_ADS_PARTNER_ID);

        CampaignPlatform platform = new CampaignPlatform();
        platform.setName(MobPlatform.iOS);

        campaign.setPlatforms(singletonList(platform));
        return campaign;
    }

    private static Campaign createDirectAutoCampaign() {
        Campaign campaign = createCommonCampaign();
        campaign.setPartnerId(DIRECT_AUTO_PARTNER_ID);
        campaign.setPlatforms(emptyList());
        campaign.setStrictAttributionWindow(StrictAttributionWindow.none);
        return campaign;
    }

    private static Campaign createOrdinaryAndroidCampaign() {
        Campaign campaign = createCommonAndroidCampaign(ORDINARY_PARTNER_ID);
        campaign.getPlatforms().get(0).setTargetUrlId(TARGET_URL_ID);
        campaign.setStrictAttributionWindow(StrictAttributionWindow.ten_days);
        return campaign;
    }

    private static Campaign createAdwordsAndroidCampaign() {
        Campaign campaign = createCommonAndroidCampaign(ADWORDS_PARTNER_ID);
        campaign.setAdwordsConversionId("123");
        campaign.setAdwordsConversionLabel("345");
        campaign.setAdwordsLinkId("546");
        campaign.setStrictAttributionWindow(StrictAttributionWindow.thirty_days);
        return campaign;
    }

    private static Campaign createCommonAndroidCampaign(long partnerId) {
        Campaign campaign = createCommonCampaign();
        campaign.setPartnerId(partnerId);

        campaign.setPlatforms(singletonList(androidPlatform()));
        return campaign;
    }

    private static Campaign createRemarketingCampaign() {
        return createMyTargetAndroidCampaign();
    }

    @NotNull
    private static CampaignPlatform androidPlatform() {
        CampaignPlatform platform = new CampaignPlatform();
        platform.setDeepLinkId(DEEP_LINK_ID);
        platform.setName(MobPlatform.android);
        return platform;
    }

    private static Campaign createCommonCampaign(long partnerId) {
        final Campaign campaign = createCommonCampaign();
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

    private Matcher<ConflictApiException> createConflictApiExceptionMatcher(String location, String description) {
        return new TypeSafeMatcher<>() {
            @Override
            protected boolean matchesSafely(ConflictApiException e) {
                return Objects.equals(location, e.getLocation()) && Objects.equals(description, e.getDescription());
            }

            @Override
            public void describeTo(Description matcherDescription) {
                matcherDescription.appendValue(location + ", " + description);
            }
        };
    }

    private static class TranslationHelperStub extends TranslationHelper {
        @Override
        public String localizeMessage(String message, Object... args) {
            return message;
        }
    }

}
