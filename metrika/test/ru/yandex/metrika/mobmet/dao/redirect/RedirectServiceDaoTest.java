package ru.yandex.metrika.mobmet.dao.redirect;

import java.util.Collections;
import java.util.List;
import java.util.Optional;

import com.google.common.collect.ImmutableMap;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.mobmet.management.conversion.MobmetConversionDao;
import ru.yandex.metrika.mobmet.management.conversion.MobmetConversionService;
import ru.yandex.metrika.mobmet.model.redirect.AppDeepLink;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.CampaignPlatform;
import ru.yandex.metrika.mobmet.model.redirect.Postback;
import ru.yandex.metrika.mobmet.model.redirect.PostbackKind;
import ru.yandex.metrika.segments.apps.misc.FingerprintAttributionWindow;
import ru.yandex.metrika.segments.apps.misc.MobPlatform;
import ru.yandex.metrika.segments.apps.misc.PartnerType;
import ru.yandex.metrika.segments.apps.misc.PartnerTypes;
import ru.yandex.metrika.segments.apps.misc.PostbackAttributionWindow;
import ru.yandex.metrika.segments.apps.misc.StrictAttributionWindow;
import ru.yandex.metrika.spring.TranslationHelper;

import static org.mockito.Matchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;


public class RedirectServiceDaoTest {

    private static final String TRACKING_ID = "0000";
    private static final int API_KEY = 2;
    private static final long DEEP_LINK_ID = 1L;
    private static final long TARGET_URL_ID = 2L;

    private final DeepLinkDao deepLinkDao = mock(DeepLinkDao.class);
    private final TargetUrlDao targetUrlDao = mock(TargetUrlDao.class);
    private final PostbackDao postbackDao = mock(PostbackDao.class);
    private final OmniPostbackDao omniPostbackDao = mock(OmniPostbackDao.class);
    private final MobmetConversionDao conversionDao = mock(MobmetConversionDao.class);
    private final MultiplatformDao multiplatformDao = mock(MultiplatformDao.class);
    private final CampaignsDao campaignsDao = mock(CampaignsDao.class);
    private final PartnerTypes partnerTypes = mock(PartnerTypes.class);
    private final TrackerPreprocessor trackerPreprocessor = new TrackerPreprocessor(campaignsDao, deepLinkDao, targetUrlDao,
            partnerTypes, null, Collections.emptyMap());
    private final TranslationHelper translationHelper = mock(TranslationHelper.class);

    private static final TrackingErrorsMessageGenerator messageGenerator =
            new TrackingErrorsMessageGenerator(new TranslationHelperStub());

    private final EmptyPlatformsFieldsProcessor emptyPlatformsFieldsProcessor = new EmptyPlatformsFieldsProcessor(multiplatformDao);
    private final CommonProcessor trackerProcessor = new CommonProcessor(
            partnerTypes,
            ImmutableMap.of(PartnerType.DOUBLECLICK, emptyPlatformsFieldsProcessor,
                    PartnerType.ADWORDS, new AdwordsFieldsProcessor(new AdwordsSettings(), emptyPlatformsFieldsProcessor),
                    PartnerType.DIRECT, new DirectFieldsProcessor(new DirectSettings()),
                    PartnerType.TIKTOK, new TiktokFieldsProcessor(messageGenerator, new TiktokSettings())));

    private final MobmetConversionService conversionService = new MobmetConversionService(conversionDao, postbackDao);
    private final RedirectServiceDao redirectServiceDao = new RedirectServiceDao(
            null, postbackDao, omniPostbackDao, campaignsDao, multiplatformDao, partnerTypes, trackerPreprocessor,
            trackerProcessor, translationHelper, conversionService);

    private final Campaign updateCampaign = new Campaign();

    @Before
    public void before() {

        final AppDeepLink deepLink = new AppDeepLink();
        deepLink.setPlatform(MobPlatform.android);

        final AppTargetUrl targetUrl = new AppTargetUrl();
        targetUrl.setPlatform(MobPlatform.android);

        when(deepLinkDao.selectOne(API_KEY, DEEP_LINK_ID)).thenReturn(deepLink);
        when(targetUrlDao.selectOne(API_KEY, TARGET_URL_ID)).thenReturn(targetUrl);
        when(partnerTypes.determineTypeForPartner(any())).thenReturn(PartnerType.ORDINARY);
        when(campaignsDao.select(TRACKING_ID, API_KEY)).thenReturn(Optional.of(new Campaign()));
        when(campaignsDao.update(any())).thenReturn(1);

        updateCampaign.setName("Name");
        updateCampaign.setApiKey(API_KEY);
        updateCampaign.setTrackingId(TRACKING_ID);
        updateCampaign.setStrictAttributionWindow(StrictAttributionWindow.nine_days);
        updateCampaign.setFingerprintAttributionWindow(FingerprintAttributionWindow.one_day);

        final CampaignPlatform platform = new CampaignPlatform();
        platform.setDeepLinkId(DEEP_LINK_ID);
        platform.setTargetUrlId(TARGET_URL_ID);
        platform.setName(MobPlatform.android);

        updateCampaign.setPlatforms(Collections.singletonList(platform));
    }

    @Test
    public void testUpdate() {
        final Postback newPostback = new Postback(null, "url", null, null, null, PostbackKind.cpa, "event", null, null, false, PostbackAttributionWindow.eight_days, false, false, 123L);
        final Postback holdPostback = new Postback(4L, "url4", null, null, null, PostbackKind.cpa, "event4", null, null, true, PostbackAttributionWindow.none, true, false, 234L);
        final Postback deletePostback = new Postback(2L, "url3", null, null, null, PostbackKind.cpi, "event3", null, null, true, PostbackAttributionWindow.seven_days, false, false, 345L);

        final Postback updateUserPostback = new Postback(1L, "newUrl", null, null, null, PostbackKind.cpa, "event2", null, null, true, PostbackAttributionWindow.eight_days, false, false, 999L);
        final Postback updateDbPostback = new Postback(1L, "url2", null, null, null, PostbackKind.cpa, "event2", null, null, true, PostbackAttributionWindow.eight_days, false, false, 999L);

        updateCampaign.setPostbacks(List.of(newPostback, updateUserPostback, holdPostback));

        when(postbackDao.select(TRACKING_ID)).thenReturn(List.of(updateDbPostback, holdPostback, deletePostback));

        redirectServiceDao.updateCampaign(updateCampaign);

        verify(postbackDao, times(1)).delete(Collections.singletonList(deletePostback));
        verify(postbackDao, times(1)).insert(Collections.singletonList(newPostback), TRACKING_ID, API_KEY);
        verify(postbackDao, times(1)).update(Collections.singletonList(updateUserPostback));
    }

    private static class TranslationHelperStub extends TranslationHelper {
        @Override
        public String localizeMessage(String message, Object... args) {
            return message;
        }
    }
}
