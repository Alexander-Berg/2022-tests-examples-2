package ru.yandex.autotests.metrika.appmetrica.tests.ft.management;

import java.io.File;
import java.net.URISyntaxException;
import java.net.URL;
import java.time.LocalDate;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.rits.cloning.Cloner;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang.RandomStringUtils;
import org.apache.commons.lang.StringUtils;
import org.joda.time.DateTimeZone;

import ru.yandex.autotests.metrika.appmetrica.actions.EditAction;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Partner;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.exceptions.AppMetricaException;
import ru.yandex.autotests.metrika.appmetrica.info.push.credentials.AppleCredentialsInfo;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials.AndroidUpdateParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials.HuaweiUpdateParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials.WinUpdateParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field;
import ru.yandex.autotests.metrika.appmetrica.utils.AdwordsConversionValues;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.mobmet.cloud.model.CloudAuthKey;
import ru.yandex.metrika.mobmet.cloud.model.CloudExport;
import ru.yandex.metrika.mobmet.cloud.model.CloudExportType;
import ru.yandex.metrika.mobmet.crash.alerts.VelocityAlertConfig;
import ru.yandex.metrika.mobmet.crash.alerts.VelocityAlertType;
import ru.yandex.metrika.mobmet.crash.alerts.settings.CrashAlertSettings;
import ru.yandex.metrika.mobmet.crash.model.CrashAlertSettingsSummary;
import ru.yandex.metrika.mobmet.dao.MobSegment;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationCreationInfo;
import ru.yandex.metrika.mobmet.management.ApplicationUpdateInfo;
import ru.yandex.metrika.mobmet.model.AppLabel;
import ru.yandex.metrika.mobmet.model.Funnel;
import ru.yandex.metrika.mobmet.model.FunnelPatternType;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.metrika.mobmet.model.TestDevice;
import ru.yandex.metrika.mobmet.model.TestDevicePurpose;
import ru.yandex.metrika.mobmet.model.TestDeviceType;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConfig;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConversionModel;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConversionModelEvent;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVEngagementModel;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVRevenueModel;
import ru.yandex.metrika.mobmet.model.cv.SKAdMeasurementTime;
import ru.yandex.metrika.mobmet.model.cv.SKAdMeasurementTimeUnit;
import ru.yandex.metrika.mobmet.model.redirect.AppDeepLink;
import ru.yandex.metrika.mobmet.model.redirect.AppTargetUrl;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.CampaignPlatform;
import ru.yandex.metrika.mobmet.model.redirect.CampaignSource;
import ru.yandex.metrika.mobmet.model.redirect.Postback;
import ru.yandex.metrika.mobmet.model.redirect.PostbackHeader;
import ru.yandex.metrika.mobmet.model.redirect.PostbackKind;
import ru.yandex.metrika.mobmet.model.redirect.PostbackMethod;
import ru.yandex.metrika.mobmet.model.redirect.PostbackTemplate;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartner;
import ru.yandex.metrika.mobmet.model.redirect.TrackingPartnerMacros;
import ru.yandex.metrika.mobmet.organization.model.Organization;
import ru.yandex.metrika.mobmet.profiles.model.ProfileCustomAttribute;
import ru.yandex.metrika.mobmet.profiles.model.ProfileStatus;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignBriefAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushHypothesisAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushMessageGroupAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushMessageGroupContentAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.model.ActionType;
import ru.yandex.metrika.mobmet.push.response.PushCredentialsSummary;
import ru.yandex.metrika.mobmet.revenue.model.RevenueAppStoreCredentials;
import ru.yandex.metrika.mobmet.revenue.model.RevenueGooglePlayCredentials;
import ru.yandex.metrika.push.HypothesisType;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;
import ru.yandex.metrika.segments.apps.misc.FingerprintAttributionWindow;
import ru.yandex.metrika.segments.apps.misc.MobPlatform;
import ru.yandex.metrika.segments.apps.misc.PostbackAttributionWindow;
import ru.yandex.metrika.segments.apps.misc.PushPlatform;
import ru.yandex.metrika.segments.apps.misc.StrictAttributionWindow;
import ru.yandex.metrika.segments.apps.misc.profile.ProfileAttributeType;

import static java.lang.String.format;
import static java.time.format.DateTimeFormatter.ISO_LOCAL_DATE;
import static java.util.Arrays.asList;
import static java.util.Collections.emptyList;
import static java.util.Collections.singletonList;
import static java.util.Collections.singletonMap;
import static java.util.stream.Collectors.toMap;
import static org.apache.commons.lang3.RandomStringUtils.randomAlphanumeric;
import static ru.yandex.autotests.irt.testutils.RandomUtils.getNextInt;
import static ru.yandex.autotests.irt.testutils.RandomUtils.getString;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_ONE_NODE_SHARD_CLUSTER;
import static ru.yandex.autotests.metrika.appmetrica.data.CloudExport.CLOUD_VALID_SERVICE_ACCOUNT;
import static ru.yandex.autotests.metrika.appmetrica.data.CommonTestData.randomColor;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.ADWORDS;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.DIRECT;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.DOUBLECLICK;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.FACEBOOK;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.HUAWEI_ADS;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.MYTARGET;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.TIKTOK;
import static ru.yandex.autotests.metrika.appmetrica.data.Partners.ZORKA;
import static ru.yandex.autotests.metrika.appmetrica.data.User.LOGIN;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.CloudExportMetaSteps.CLIENT_EVENTS_TABLE;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestDataSecrets.getYcEditorPrivateKey;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestDataSecrets.getYcViewerPrivateKey;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.APNS_COLLAPSE_ID;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.ATTACHMENTS;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.BADGE;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.BANNER;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.CATEGORY;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.CHANNEL_ID;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.COLLAPSE_KEY;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.DATA;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.EXPIRATION;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.ICON;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.ICON_BACKGROUND;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.IMAGE;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.LED_COLOR;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.LED_INTERVAL;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.LED_PAUSE_INTERVAL;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.MUTABLE_CONTENT;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.PRIORITY;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.SOUND;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.TEXT;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.THREAD_ID;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.TIME_TO_LIVE;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.TITLE;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.URGENCY;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign.Field.VIBRATION;
import static ru.yandex.metrika.mobmet.model.TestDevicePurpose.REATTRIBUTION;
import static ru.yandex.metrika.mobmet.model.TestDeviceType.GOOGLE_AID;
import static ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaignBriefInnerSendTimePolicy.DELAYED;
import static ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaignBriefInnerSendTimePolicy.NOW;
import static ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaignBriefInnerTimeZoneType.APPLICATION;
import static ru.yandex.metrika.mobmet.push.common.campaigns.model.PushCampaignBriefInnerTimeZoneType.DEVICE;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_CLIENT;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_PROTOBUF_CRASH;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_PROTOBUF_ERROR;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_REVENUE;
import static ru.yandex.metrika.segments.apps.misc.SKAdCVModelType.CONVERSION;
import static ru.yandex.metrika.segments.apps.misc.SKAdCVModelType.ENGAGEMENT;
import static ru.yandex.metrika.segments.apps.misc.SKAdCVModelType.NOT_CONFIGURED;
import static ru.yandex.metrika.segments.apps.misc.SKAdCVModelType.REVENUE;

/**
 * Created by konkov on 15.09.2016.
 */
public final class TestData {

    // region constants

    public static final String ADWORDS_CONVERSION_ID = "716057272";

    public static final String ADWORDS_CONVERSION_LABEL = "adwords";

    public static final String ADWORDS_LINK_ID = "ADWORDSLINKID23";

    public static final String FACEBOOK_DECRYPTION_KEY =
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";

    public static final String HUAWEI_LINK_ID = "HUAWEILINKID23";

    private static final String APPLICATION_BASE_NAME = "Тестовое приложение ";

    private static final String LABEL_BASE_NAME = "Тестовая папка ";

    private static final String PARTNER_BASE_NAME = "Тестовый партнер ";

    private static final String PUSH_CAMPAIGN_BASE_NAME = "Тестовая кампания ";

    private static final String TRACKER_BASE_NAME = "Тестовый трекер ";

    public static final String TARGET_URL_NAME = "Целевая ссылка ";

    public static final String DEEP_LINK_NAME = "Deep link ";

    public static final String POSTBACK_TEMPLATE_NAME = "Шаблон постбека ";

    public static final String TEST_DEVICE_NAME = "Тестовое устройство ";

    public static final String TEST_SEGMENT_NAME = "Тестовый сегмент ";

    public static final String TEST_FUNNEL_NAME = "Тестовая воронка ";

    public static final String TEST_EVENT_NAME = "Тестовое событие ";

    public static final String TEST_EVENT_COMMENT = "Тестовый комментарий события ";

    public static final String TEST_CRASH_COMMENT = "Тестовый комментарий крэша ";

    public static final String TEST_DEVICE_ID = "Test device ID ";

    public static final String NOTIFICATION_EMAIL_SUFFIX = "@yandex.ru";

    public static final String TEAM_ID = "TeamID ";

    public static final String URL_ADDRESS_EXAMPLE = "http://example.com";

    private static final String PUSH_HYPOTHESIS_NAME = "Пуш гипотеза";

    private static final String TEST_PROFILE_ATTRIBUTE_NAME = "Тестовый атрибут профиля ";

    private static final int RANDOM_STRING_LENGTH = 10;

    private static final long APPLICATION_CATEGORY_1 = 85;

    private static final long APPLICATION_CATEGORY_2 = 88;

    private static final String DEFAULT_GOOGLE_KEY =
            "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCqGKukO1De7zhZj6+H0qtjTkVxwTCpvKe4eCZ0" +
                    "FPqri0cb2JZfXJ/DgYSF6vUpwmJG8wVQZKjeGcjDOL5UlsuusFncCzWBQ7RKNUSesmQRMSGkVb1/" +
                    "3j+skZ6UtW+5u09lHNsj6tQ51s1SPrCBkedbNf0Tp0GbMJDyR4e9T04ZZwIDAQAB";

    private static final String DEFAULT_APPLE_SHARED_SECRET = "123456789012345678901234567890ab";

    public static final String BUNDLE_ID_TEMPLATE = "ru.yandex.autotest.";

    public static final String TIKTOK_APP_ID = "Test TikTok App ID 12345";

    // endregion

    // region names

    public static String getApplicationName() {
        return APPLICATION_BASE_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static String getLabelName() {
        return LABEL_BASE_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static String getPartnerName() {
        return PARTNER_BASE_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static boolean isTestPartnerName(String partnerName) {
        return partnerName.startsWith(PARTNER_BASE_NAME);
    }

    public static String getTrackerName() {
        return TRACKER_BASE_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static boolean isTestTrackerName(String trackingName) {
        return trackingName.startsWith(TRACKER_BASE_NAME);
    }

    private static String getTargetUrlName() {
        return TARGET_URL_NAME + getString(RANDOM_STRING_LENGTH);
    }

    private static String getDeepLinkName() {
        return DEEP_LINK_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static String getPushCampaignName() {
        return PUSH_CAMPAIGN_BASE_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static String getPostbackTemplateName() {
        return POSTBACK_TEMPLATE_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static String randomUrlAddress() {
        return URL_ADDRESS_EXAMPLE + getString(RANDOM_STRING_LENGTH);
    }

    /**
     * Уникальность постбеков вычисляется по урлу. Поэтому чтобы тесты не мешали друг другу они должны быть случайными
     */
    public static String getPostbackTemplateUrl() {
        return randomUrlAddress();
    }

    public static String getTestDeviceName() {
        return TEST_DEVICE_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static String getTestDeviceId() {
        return TEST_DEVICE_ID + getString(RANDOM_STRING_LENGTH);
    }

    public static String getBundleId() {
        return BUNDLE_ID_TEMPLATE + getString(RANDOM_STRING_LENGTH);
    }

    public static String getNotificationEmail() {
        // Используем email тестового пользователя, чтобы случайно кому-нибудь не отправить письмо
        return SIMPLE_USER.get(LOGIN) + NOTIFICATION_EMAIL_SUFFIX;
    }

    public static RevenueGooglePlayCredentials getDefaultRevenueGoogleCredentials() {
        return new RevenueGooglePlayCredentials()
                .withVerificationEnabled(true)
                .withPublicKey(DEFAULT_GOOGLE_KEY);
    }

    public static RevenueAppStoreCredentials getDefaultRevenueAppStoreCredentials() {
        return new RevenueAppStoreCredentials()
                .withVerificationEnabled(true)
                .withSharedSecret(DEFAULT_APPLE_SHARED_SECRET);
    }

    public static String getTeamId() {
        return TEAM_ID + getString(RANDOM_STRING_LENGTH);
    }

    public static String eventLabel(int index) {
        return String.format("foo_%s", index);
    }

    public static String getProfileAttributeName() {
        return TEST_PROFILE_ATTRIBUTE_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static String getTestSegmentName() {
        return TEST_SEGMENT_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static String getTestFunnelName() {
        return TEST_FUNNEL_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static String getTestEventName() {
        return TEST_EVENT_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static String getTestEventComment() {
        return TEST_EVENT_COMMENT + getString(RANDOM_STRING_LENGTH);
    }

    public static String getTestCrashComment() {
        return TEST_CRASH_COMMENT + getString(RANDOM_STRING_LENGTH);
    }

    public static long getDefaultApplicationCategory() {
        return APPLICATION_CATEGORY_1;
    }

    public static long getUpdatedApplicationCategory() {
        return APPLICATION_CATEGORY_2;
    }

    public static String getCrashGroupId() {
        return Long.toUnsignedString((long) getNextInt() << 32 | getNextInt() & 0xFFFFFFFFL);
    }

    // endregion

    // region edit actions

    public static EditAction<Application, ApplicationUpdateInfo> changeApplicationName() {
        final String newName = getApplicationName();

        return new EditAction<Application, ApplicationUpdateInfo>(
                format("Сменить название приложения на %s", newName)) {
            @Override
            public ApplicationUpdateInfo getUpdate(Application source) {
                return new ApplicationUpdateInfo()
                        .withCategory(source.getCategory())
                        .withName(newName);
            }

            @Override
            public Application edit(Application source) {
                return new Cloner().deepClone(source)
                        .withName(newName)
                        .withPermission(null)
                        .withAllowedPartners(null);
            }
        };
    }

    public static EditAction<Application, ApplicationUpdateInfo> failToChangeApplicationName() {
        final String newName = getApplicationName();

        return new EditAction<Application, ApplicationUpdateInfo>(
                format("Сменить название приложения на %s и ожидать старое название", newName)) {
            @Override
            public ApplicationUpdateInfo getUpdate(Application source) {
                return new ApplicationUpdateInfo()
                        .withCategory(source.getCategory())
                        .withName(newName);
            }

            @Override
            public Application edit(Application source) {
                return new Cloner().deepClone(source)
                        .withPermission(null)
                        .withAllowedPartners(null);
            }
        };
    }

    public static EditAction<Application, ApplicationUpdateInfo> changeBundleId() {
        final String newBundleId = getBundleId();

        return new EditAction<Application, ApplicationUpdateInfo>(
                format("Сменить BundleID приложения на %s", newBundleId)) {
            @Override
            public ApplicationUpdateInfo getUpdate(Application source) {
                return new ApplicationUpdateInfo()
                        .withCategory(source.getCategory())
                        .withBundleId(newBundleId);
            }

            @Override
            public Application edit(Application source) {
                return new Cloner().deepClone(source)
                        .withBundleId(newBundleId)
                        .withPermission(null)
                        .withAllowedPartners(null);
            }
        };
    }

    public static EditAction<Application, ApplicationUpdateInfo> changeNotificationEmail(String newEmail) {

        return new EditAction<Application, ApplicationUpdateInfo>(
                format("Сменить email приложения на %s", newEmail)) {
            @Override
            public ApplicationUpdateInfo getUpdate(Application source) {
                return new ApplicationUpdateInfo()
                        .withCategory(source.getCategory())
                        .withNotificationEmail(newEmail);
            }

            @Override
            public Application edit(Application source) {
                return new Cloner().deepClone(source)
                        .withNotificationEmail(newEmail)
                        .withPermission(null)
                        .withAllowedPartners(null);
            }
        };
    }

    public static EditAction<Application, ApplicationUpdateInfo> changeTeamId() {
        final String newTeamId = getTeamId();

        return new EditAction<Application, ApplicationUpdateInfo>(
                format("Сменить TeamID приложения на %s", newTeamId)) {
            @Override
            public ApplicationUpdateInfo getUpdate(Application source) {
                return new ApplicationUpdateInfo()
                        .withCategory(source.getCategory())
                        .withTeamId(newTeamId);
            }

            @Override
            public Application edit(Application source) {
                return new Cloner().deepClone(source)
                        .withTeamId(newTeamId)
                        .withPermission(null)
                        .withAllowedPartners(null);
            }
        };
    }

    public static EditAction<Application, ApplicationUpdateInfo> enableGdprAgreementAccepted() {
        return new EditAction<Application, ApplicationUpdateInfo>("Принять соглашение GDPR") {
            @Override
            public ApplicationUpdateInfo getUpdate(Application source) {
                return new ApplicationUpdateInfo()
                        .withCategory(source.getCategory())
                        .withGdprAgreementAccepted(true);
            }

            @Override
            public Application edit(Application source) {
                return new Cloner().deepClone(source)
                        .withGdprAgreementAccepted(true)
                        .withPermission(null)
                        .withAllowedPartners(null);
            }
        };
    }

    public static EditAction<Application, ApplicationUpdateInfo> changeCategory(Long newCategory) {
        return new EditAction<Application, ApplicationUpdateInfo>("Выбрать категорию приложения") {
            @Override
            public ApplicationUpdateInfo getUpdate(Application source) {
                return new ApplicationUpdateInfo()
                        .withCategory(source.getCategory())
                        .withCategory(newCategory);
            }

            @Override
            public Application edit(Application source) {
                return new Cloner().deepClone(source)
                        .withCategory(newCategory)
                        .withPermission(null)
                        .withAllowedPartners(null);
            }
        };
    }

    public static EditAction<Application, ApplicationUpdateInfo> enableUseUniversalLinks() {
        return new EditAction<Application, ApplicationUpdateInfo>("Включить настройку UseUniversalLinks приложения") {
            @Override
            public ApplicationUpdateInfo getUpdate(Application source) {
                return new ApplicationUpdateInfo()
                        .withCategory(source.getCategory())
                        .withUseUniversalLinks(true);
            }

            @Override
            public Application edit(Application source) {
                return new Cloner().deepClone(source)
                        .withUseUniversalLinks(true)
                        .withPermission(null)
                        .withAllowedPartners(null);
            }
        };
    }

    public static EditAction<Application, ApplicationUpdateInfo> enableHideAddressSetting() {
        return new EditAction<Application, ApplicationUpdateInfo>("Включить настройку HideAddress приложения") {
            @Override
            public ApplicationUpdateInfo getUpdate(Application source) {
                return new ApplicationUpdateInfo()
                        .withCategory(source.getCategory())
                        .withHideAddress(true);
            }

            @Override
            public Application edit(Application source) {
                return new Cloner().deepClone(source)
                        .withHideAddress(true)
                        .withPermission(null)
                        .withAllowedPartners(null);
            }
        };
    }

    public static EditAction<Application, ApplicationUpdateInfo> changeTimeZone(TimeZoneInfo timeZone) {
        return new EditAction<Application, ApplicationUpdateInfo>(
                format("Сменить часовой пояс на %s", timeZone)) {
            @Override
            public ApplicationUpdateInfo getUpdate(Application source) {
                return new ApplicationUpdateInfo()
                        .withCategory(source.getCategory())
                        .withTimeZoneName(timeZone.getName());
            }

            @Override
            public Application edit(Application source) {
                return new Cloner().deepClone(source)
                        .withTimeZoneName(timeZone.getName())
                        .withTimeZoneOffset(timeZone.getOffset())
                        .withPermission(null)
                        .withAllowedPartners(null);
            }
        };
    }

    public static EditAction<Application, ApplicationUpdateInfo> failToChangeTimeZone(TimeZoneInfo timeZone) {
        return new EditAction<Application, ApplicationUpdateInfo>(
                format("Сменить часовой пояс на %s и ожидать старый часовой пояс", timeZone)) {
            @Override
            public ApplicationUpdateInfo getUpdate(Application source) {
                return new ApplicationUpdateInfo()
                        .withCategory(source.getCategory())
                        .withTimeZoneName(timeZone.getName());
            }

            @Override
            public Application edit(Application source) {
                return new Cloner().deepClone(source)
                        .withPermission(null)
                        .withAllowedPartners(null);
            }
        };
    }

    public static EditAction<Campaign, Campaign> changeTrackerName() {
        final String newName = getTrackerName();

        return new EditAction<Campaign, Campaign>(
                format("Сменить название трекера на %s", newName)) {
            @Override
            public Campaign getUpdate(Campaign source) {
                return edit(source);
            }

            @Override
            public Campaign edit(Campaign source) {
                return new Cloner().deepClone(source)
                        .withUpdateTime(null)
                        .withName(newName);
            }
        };
    }

    /**
     * Идея итентична {@link #changeTrackerToMultiplatform(UserSteps)}
     */
    public static EditAction<Campaign, Campaign> changeTrackerToFallback(UserSteps owner) {

        return new EditAction<Campaign, Campaign>("Поменять платформы трекера на fallback") {
            @Override
            public Campaign getUpdate(Campaign source) {
                return edit(source);
            }

            @Override
            public Campaign edit(Campaign source) {
                CampaignPlatform fallbackPlatform = defaultPlatform(MobPlatform.FALLBACK);
                AppTargetUrl targetUrl = owner.onTrackerSteps()
                        .getOrCreateTargetUrl(source.getApiKey(), defaultTargetUrl(fallbackPlatform.getName()));
                fallbackPlatform.setTargetUrlId(targetUrl.getId());
                return new Cloner().deepClone(source)
                        .withUpdateTime(null)
                        .withPlatforms(singletonList(fallbackPlatform));
            }
        };
    }

    /**
     * Для того что бы поменять платформы для них надо вначале создать целевые ссылки. Так как мы не создаем
     * повторно одни и те же ссылки, если они уже есть, то методы edit и getUpdate вернут корректные
     * идентификаторы целевых ссылок.
     */
    public static EditAction<Campaign, Campaign> changeTrackerToMultiplatform(UserSteps owner) {

        return new EditAction<Campaign, Campaign>("Поменять платформы трекера на несколько платформ") {

            @Override
            public Campaign getUpdate(Campaign source) {
                return edit(source);
            }

            @Override
            public Campaign edit(Campaign source) {
                List<CampaignPlatform> platforms = asList(
                        defaultPlatform(MobPlatform.FALLBACK),
                        defaultPlatform(MobPlatform.ANDROID),
                        defaultPlatform(MobPlatform.I_OS));
                platforms.forEach(platform -> {
                    AppTargetUrl targetUrl = owner.onTrackerSteps()
                            .getOrCreateTargetUrl(source.getApiKey(), defaultTargetUrl(platform.getName()));
                    platform.setTargetUrlId(targetUrl.getId());
                });
                return new Cloner().deepClone(source)
                        .withUpdateTime(null)
                        .withPlatforms(platforms);
            }
        };
    }

    public static EditAction<Campaign, Campaign> changeTrackerPostbacks() {
        return changeTrackerPostbacks(defaultPostback(), defaultPostback());
    }

    public static EditAction<Campaign, Campaign> changeTrackerPostbacks(Postback... newPostbacks) {

        final List<Postback> postbacks = asList(newPostbacks);

        return new EditAction<Campaign, Campaign>("Изменить список постбеков") {
            @Override
            public Campaign getUpdate(Campaign source) {
                return edit(source);
            }

            @Override
            public Campaign edit(Campaign source) {
                return new Cloner().deepClone(source)
                        .withUpdateTime(null)
                        .withPostbacks(postbacks);
            }
        };
    }

    public static EditAction<Campaign, Campaign> changeTrackerPostbackContents() {
        final String newUrl = randomUrlAddress();

        return new EditAction<Campaign, Campaign>("Изменить содержимое постбека") {
            @Override
            public Campaign getUpdate(Campaign source) {
                return edit(source);
            }

            @Override
            public Campaign edit(Campaign source) {
                Campaign clone = new Cloner().deepClone(source)
                        .withUpdateTime(null);
                clone.getPostbacks().get(0).withUrl(newUrl);
                return clone;
            }
        };
    }

    public static EditAction<Campaign, Campaign> changeTrackerFacebookDecryptionKey(String decryptionKey) {
        return new EditAction<Campaign, Campaign>(
                format("Сменить Facebook Decryption Key трекера на %s", decryptionKey)) {
            @Override
            public Campaign getUpdate(Campaign source) {
                return edit(source);
            }

            @Override
            public Campaign edit(Campaign source) {
                return new Cloner().deepClone(source)
                        .withUpdateTime(null)
                        .withFacebookDecryptionKey(decryptionKey);
            }
        };
    }

    public static EditAction<Campaign, Campaign> changeTrackerConversion(AdwordsConversionValues conversion) {
        return new EditAction<Campaign, Campaign>(
                format("Сменить Google Ads конверсию трекера на %s", conversion.toString())) {
            @Override
            public Campaign getUpdate(Campaign source) {
                return edit(source);
            }

            @Override
            public Campaign edit(Campaign source) {
                return new Cloner().deepClone(source)
                        .withUpdateTime(null)
                        .withAdwordsConversionId(conversion.getConversionId())
                        .withAdwordsConversionLabel(conversion.getConversionLabel())
                        .withAdwordsLinkId(conversion.getLinkId());
            }
        };
    }

    public static EditAction<TestDevice, TestDevice> changeTestDeviceName() {
        final String newName = getTestDeviceName();

        return new EditAction<TestDevice, TestDevice>(
                format("Сменить название тестового устройства на %s", newName)) {
            @Override
            public TestDevice getUpdate(TestDevice source) {
                return edit(source);
            }

            @Override
            public TestDevice edit(TestDevice source) {
                return new Cloner().deepClone(source)
                        .withName(newName);
            }
        };
    }

    public static EditAction<TestDevice, TestDevice> changeTestDeviceId() {
        final String newId = getTestDeviceId();

        return new EditAction<TestDevice, TestDevice>(
                format("Сменить ID тестового устройства на %s", newId)) {
            @Override
            public TestDevice getUpdate(TestDevice source) {
                return edit(source);
            }

            @Override
            public TestDevice edit(TestDevice source) {
                return new Cloner().deepClone(source)
                        .withDeviceId(newId);
            }
        };
    }

    public static EditAction<TestDevice, TestDevice> changeTestDevicePurpose(TestDevicePurpose purpose) {
        return new EditAction<TestDevice, TestDevice>(
                format("Сменить назначение тестового устройства на %s", purpose)) {
            @Override
            public TestDevice getUpdate(TestDevice source) {
                return edit(source);
            }

            @Override
            public TestDevice edit(TestDevice source) {
                return new Cloner().deepClone(source)
                        .withPurpose(purpose);
            }
        };
    }

    public static EditAction<TestDevice, TestDevice> changeTestDeviceType(TestDeviceType type) {
        return new EditAction<TestDevice, TestDevice>(
                format("Сменить тип тестового устройства на %s", type)) {
            @Override
            public TestDevice getUpdate(TestDevice source) {
                return edit(source);
            }

            @Override
            public TestDevice edit(TestDevice source) {
                return new Cloner().deepClone(source)
                        .withType(type);
            }
        };
    }

    public static EditAction<MobmetGrantE, MobmetGrantE> changePartner() {
        final List<Long> newPartners = ImmutableList.of(DIRECT.get(Partner.ID));

        return new EditAction<MobmetGrantE, MobmetGrantE>(
                format("Сменить список разрешенных партнеров на %s", newPartners)) {
            @Override
            public MobmetGrantE getUpdate(MobmetGrantE source) {
                return edit(source);
            }

            @Override
            public MobmetGrantE edit(MobmetGrantE source) {
                return new Cloner().deepClone(source)
                        .withPartners(newPartners);
            }
        };
    }

    public static EditAction<MobmetGrantE, MobmetGrantE> changeEvents() {
        final List<String> newEvents = ImmutableList.of(eventLabel(42), eventLabel(46));

        return new EditAction<MobmetGrantE, MobmetGrantE>(
                format("Сменить список разрешенных событий на %s", newEvents)) {
            @Override
            public MobmetGrantE getUpdate(MobmetGrantE source) {
                return edit(source);
            }

            @Override
            public MobmetGrantE edit(MobmetGrantE source) {
                return new Cloner().deepClone(source)
                        .withEventLabels(newEvents);
            }
        };
    }

    public static EditAction<MobmetGrantE, MobmetGrantE> changeGrantType() {
        final GrantType newGrantType = GrantType.EDIT;

        return new EditAction<MobmetGrantE, MobmetGrantE>(
                format("Сменить тип доступа на %s", newGrantType)) {
            @Override
            public MobmetGrantE getUpdate(MobmetGrantE source) {
                return edit(source);
            }

            @Override
            public MobmetGrantE edit(MobmetGrantE source) {
                return new Cloner().deepClone(source)
                        .withPerm(newGrantType)
                        .withPartners(Collections.emptyList())
                        .withEventLabels(Collections.emptyList());
            }
        };
    }

    public static EditAction<TrackingPartner, TrackingPartner> changePartnerName() {
        final String newPartnerName = getPartnerName();

        return new EditAction<TrackingPartner, TrackingPartner>(
                format("Сменить название партнера на %s", newPartnerName)) {
            @Override
            public TrackingPartner getUpdate(TrackingPartner source) {
                return edit(source);
            }

            @Override
            public TrackingPartner edit(TrackingPartner source) {
                return new Cloner().deepClone(source)
                        .withName(newPartnerName);
            }
        };
    }

    public static EditAction<PostbackTemplate, PostbackTemplate> changePostbackTemplateName() {
        final String newTemplateName = getPostbackTemplateName();

        return new EditAction<PostbackTemplate, PostbackTemplate>(
                format("Сменить название шаблона постбека на %s", newTemplateName)) {
            @Override
            public PostbackTemplate getUpdate(PostbackTemplate source) {
                return edit(source);
            }

            @Override
            public PostbackTemplate edit(PostbackTemplate source) {
                return new Cloner().deepClone(source)
                        .withTitle(newTemplateName);
            }
        };
    }

    public static EditAction<PostbackTemplate, PostbackTemplate> changePostbackTemplateParams(
            PostbackMethod method,
            List<PostbackHeader> headers,
            String body
    ) {
        return new EditAction<PostbackTemplate, PostbackTemplate>(
                format("Сменить параметры шаблона постбека на %s, %s, %s", method, headers, body)) {
            @Override
            public PostbackTemplate getUpdate(PostbackTemplate source) {
                return edit(source);
            }

            @Override
            public PostbackTemplate edit(PostbackTemplate source) {
                return new Cloner().deepClone(source)
                        .withMethod(method)
                        .withHeaders(headers)
                        .withBody(body);
            }
        };
    }

    public static EditAction<Campaign, Campaign> changeTiktokAppId() {
        return new EditAction<Campaign, Campaign>(
                format("Сменить tiktok_app_id трекера на %s", TIKTOK_APP_ID)) {
            @Override
            public Campaign getUpdate(Campaign source) {
                return new Cloner().deepClone(source)
                        .withTiktokAppId(TIKTOK_APP_ID);
            }

            @Override
            public Campaign edit(Campaign source) {
                Campaign clone = new Cloner().deepClone(source)
                        .withTiktokAppId(TIKTOK_APP_ID);
                clone.getPostbacks().forEach(
                        p -> p.setBody("{\"context\":{\"app\":{\"tiktok_app_id\":\"" + TIKTOK_APP_ID + "\"}}}"));
                return clone;
            }
        };
    }

    public static EditAction<Campaign, Campaign> changeHuaweiLinkId(String huaweiLinkId) {
        return new EditAction<>(
                format("Сменить huawei_link_id трекера на %s", huaweiLinkId)) {
            @Override
            public Campaign getUpdate(Campaign source) {
                return edit(source);
            }

            @Override
            public Campaign edit(Campaign source) {
                return new Cloner().deepClone(source)
                        .withUpdateTime(null)
                        .withHuaweiLinkId(huaweiLinkId);
            }
        };
    }


    // endregion

    // region predefined entities

    public static Organization defaultOrganization(long ownerUid) {
        var organization = new Organization();
        organization.setName(getString(RANDOM_STRING_LENGTH));
        organization.setOwnerUid(ownerUid);
        return organization;
    }

    public static ApplicationCreationInfo getDefaultApplication() {
        return new ApplicationCreationInfo()
                .withCategory(getDefaultApplicationCategory())
                .withName(getApplicationName());
    }

    public static ApplicationCreationInfo getApplicationWithAppNamePrefix(String prefix) {
        return getDefaultApplication().withName(prefix + getApplicationName());
    }

    public static ApplicationCreationInfo getApplicationWithoutCategory() {
        return new ApplicationCreationInfo().withName(getApplicationName());
    }

    public static ApplicationCreationInfo getApplicationWithTimezone(TimeZoneInfo timeZoneInfo) {
        return getDefaultApplication().withTimeZoneName(timeZoneInfo.getName());
    }

    public static ApplicationCreationInfo getApplicationWithTimezoneName(String timeZoneName) {
        return getDefaultApplication().withTimeZoneName(timeZoneName);
    }

    public static ApplicationCreationInfo getApplicationWithGDPRAgreementAccepted() {
        return getDefaultApplication().withGdprAgreementAccepted(true);
    }

    public static ApplicationCreationInfo getApplicationWithEmail() {
        return getDefaultApplication().withNotificationEmail(getNotificationEmail());
    }

    public static Application getExpectedApplication(User user, ApplicationCreationInfo appToAdd) {
        return new Application()
                .withCategory(getDefaultApplicationCategory())
                .withName(appToAdd.getName())
                .withOwnerLogin(user.get(LOGIN))
                .withTimeZoneName(appToAdd.getTimeZoneName())
                .withLabelId(appToAdd.getLabelId());
    }

    public static AppLabel getDefaultLabel() {
        return new AppLabel().withName(getLabelName());
    }

    public static PushCampaignAdapter silentCampaignWithSingleMessage(PushPlatform platform) {
        return silentCampaign()
                .withHypotheses(singletonList(singlePlatformHypothesis(platform)));
    }

    public static PushCampaignAdapter campaignWithSingleMessage(PushPlatform platform) {
        return minimalCampaign()
                .withHypotheses(singletonList(singlePlatformHypothesis(platform)));
    }

    public static PushCampaignAdapter updateMessagesContent(PushCampaignAdapter target,
                                                            Map<Field, Object> notificationContent) {
        target.getHypotheses()
                .forEach(h -> h.getMessages().values().stream()
                        .flatMap(m -> m.getContents().values().stream())
                        .forEach(m -> m.setContent(
                                mapContentFields(notificationContent)
                        )));
        return target;
    }

    private static Map<String, Object> mapContentFields(Map<Field, Object> content) {
        return content.entrySet().stream()
                .collect(toMap(
                        e -> e.getKey().getFieldName(),
                        Map.Entry::getValue
                ));
    }

    public static PushHypothesisAdapter singlePlatformHypothesis(PushPlatform platform) {
        return new PushHypothesisAdapter()
                .withName(PUSH_HYPOTHESIS_NAME)
                .withShare(1.0)
                .withType(HypothesisType.ALTERNATIVE)
                .withMessages(singletonMap(platform, singleMessage()));
    }

    public static PushMessageGroupAdapter singleMessage() {
        return new PushMessageGroupAdapter()
                .withActionType(ActionType.OPEN_APP)
                .withContents(singletonMap("ru", pushEmptyContent()))
                .withEnabled(true);
    }

    public static Map<Field, Object> fullAndroidContent() {
        return ImmutableMap.<Field, Object>builder()
                .put(TEXT, "text")
                .put(TITLE, "title")
                .put(ICON, "icon")
                .put(ICON_BACKGROUND, randomColor())
                .put(IMAGE, "http://image")
                .put(DATA, "data")
                .put(SOUND, "default")
                .put(VIBRATION, asList(0, 100, 250, 500))
                .put(LED_COLOR, randomColor(false))
                .put(LED_INTERVAL, 1000)
                .put(LED_PAUSE_INTERVAL, 2000)
                .put(TIME_TO_LIVE, 3600)
                .put(COLLAPSE_KEY, getNextInt())
                .put(CHANNEL_ID, "channel")
                .put(BANNER, "http://banner")
                .put(URGENCY, "high")
                .build();
    }

    public static Map<Field, Object> fullIOsContent() {
        return ImmutableMap.<Field, Object>builder()
                .put(TEXT, "text")
                .put(TITLE, "title")
                .put(BADGE, getNextInt())
                .put(EXPIRATION, 3600)
                .put(PRIORITY, 5)
                .put(DATA, "data")
                .put(SOUND, "default")
                .put(MUTABLE_CONTENT, getNextInt(2))
                .put(CATEGORY, "category")
                .put(THREAD_ID, "threadId")
                .put(APNS_COLLAPSE_ID, "AppMetCollapseId_34587365345435_2345713876534")
                .put(ATTACHMENTS, ImmutableList.of(
                        ImmutableMap.of(
                                "id", "id1",
                                "file_url", "https://a.com/1.jpg",
                                "file_type", "jpg"),
                        ImmutableMap.of(
                                "id", "id2",
                                "file_url", "https://a.com/2.png",
                                "file_type", "png")))
                .build();
    }

    private static PushMessageGroupContentAdapter pushEmptyContent() {
        return new PushMessageGroupContentAdapter()
                .withDefault(true);
    }

    public static PushCampaignAdapter minimalCampaign() {
        return defaultPushCampaign(Applications.PUSH_SAMPLE.get(ID));
    }

    public static PushCampaignAdapter campaignForLargeApplication() {
        return defaultPushCampaign(Applications.YANDEX_METRO.get(ID));
    }

    public static PushCampaignAdapter silentCampaign() {
        return defaultPushCampaign(Applications.PUSH_SAMPLE.get(ID))
                .withSilent(true);
    }

    public static PushCampaignAdapter delayedCampaignWithAppTimeZone() {
        return defaultPushCampaign(Applications.PUSH_SAMPLE.get(ID))
                .withSendTimePolicy(DELAYED)
                .withSendTime("2017-09-07T12:36:33")
                .withTimeZoneType(APPLICATION);
    }

    public static PushCampaignAdapter delayedCampaignWithDeivcesTimeZone() {
        return defaultPushCampaign(Applications.PUSH_SAMPLE.get(ID))
                .withSendTimePolicy(DELAYED)
                .withSendTime("2017-09-07T12:36:33")
                .withTimeZoneType(DEVICE);
    }

    private static PushCampaignAdapter defaultPushCampaign(Long appId) {
        return new PushCampaignAdapter()
                .withAppId(appId)
                .withName(getPushCampaignName())
                .withSendTimePolicy(NOW)
                .withTimeZoneType(APPLICATION)
                .withAvailableCredentials(null); // Это поле -- output only
    }

    public static PushCampaignBriefAdapter briefInfo(PushCampaignAdapter fullInfo) {
        return new PushCampaignBriefAdapter()
                .withAppId(fullInfo.getAppId())
                .withName(fullInfo.getName())
                .withSendTimePolicy(fullInfo.getSendTimePolicy())
                .withTimeZoneType(fullInfo.getTimeZoneType())
                .withSilent(fullInfo.getSilent());
    }

    public static AppTargetUrl defaultTargetUrl() {
        return new AppTargetUrl()
                .withPlatform(MobPlatform.ANDROID)
                .withTitle(getTargetUrlName())
                .withUrl(randomUrlAddress());
    }

    public static AppTargetUrl defaultTargetUrl(MobPlatform platform) {
        return new AppTargetUrl()
                .withPlatform(platform)
                .withTitle(getTargetUrlName())
                .withUrl(makePlatformUrl(platform));
    }

    public static AppDeepLink defaultDeepLink(MobPlatform platform) {
        return new AppDeepLink()
                .withPlatform(platform)
                .withTitle(getDeepLinkName())
                .withUrl(makePlatformUrl(platform));
    }

    private static String makePlatformUrl(MobPlatform platform) {
        return "http://example_" + platform.toString() + ".com";
    }

    public static CampaignPlatform defaultPlatform(MobPlatform platform) {
        return new CampaignPlatform().withName(platform);
    }

    public static Campaign defaultTracker() {
        return tracker(null, ZORKA.get(Partner.ID), null);
    }

    public static Campaign defaultMultiplatformTracker() {
        return tracker(null, ZORKA.get(Partner.ID), null)
                .withPlatforms(asList(
                        defaultPlatform(MobPlatform.FALLBACK),
                        defaultPlatform(MobPlatform.ANDROID),
                        defaultPlatform(MobPlatform.I_OS)));
    }

    public static Campaign defaultTrackerWithMandatoryPostback() {
        return tracker(null, ZORKA.get(Partner.ID), null)
                .withPostbacks(singletonList(mandatoryPostback()));
    }

    public static Campaign facebookTracker() {
        return tracker(null, FACEBOOK.get(Partner.ID), null);
    }

    public static String randomFacebookDecryptionKey() {
        // 64 digit case-insensitive hex
        return RandomStringUtils.random(64, "0123456789abcdefABCDEF");
    }

    public static Campaign facebookTrackerWithDecryptionKey() {
        return facebookTrackerWithDecryptionKey(FACEBOOK_DECRYPTION_KEY);
    }

    public static Campaign facebookTrackerWithDecryptionKey(String decryptionKey) {
        return tracker(null, FACEBOOK.get(Partner.ID), null)
                .withFacebookDecryptionKey(decryptionKey);
    }

    public static Campaign huaweiAdsTracker() {
        return huaweiAdsTracker(HUAWEI_LINK_ID);
    }

    public static Campaign huaweiAdsTracker(String linkId) {
        return tracker(null, HUAWEI_ADS.get(Partner.ID), null)
                .withPlatforms(emptyList())
                .withHuaweiLinkId(linkId);
    }

    public static String randomHuaweiLinkId() {
        return randomAlphanumeric(10);
    }

    public static Campaign mytargetTracker() {
        return tracker(null, MYTARGET.get(Partner.ID), null);
    }

    public static Campaign remarketingMyTargetTracker() {
        return tracker(null, MYTARGET.get(Partner.ID), null)
                .withRemarketingEnabled(true)
                .withPlatforms(singletonList(defaultPlatform(MobPlatform.ANDROID)));
    }

    public static Campaign remarketingWithSmartLinksTracker() {
        return tracker(null, ZORKA.get(Partner.ID), null)
                .withRemarketingEnabled(true)
                .withRemarketingWithSmartlinks(true)
                .withPlatforms(asList(defaultPlatform(MobPlatform.ANDROID), defaultPlatform(MobPlatform.I_OS)));
    }

    public static Campaign tiktokTrackerWithPostback() {
        return tracker(null, TIKTOK.get(Partner.ID), null)
                .withPostbacks(singletonList(tiktokPostback()))
                .withPlatforms(singletonList(defaultPlatform(MobPlatform.ANDROID)));
    }

    public static Campaign directTracker() {
        return tracker(null, DIRECT.get(Partner.ID), null);
    }

    public static Campaign remarketingDirectMultiplatformTracker() {
        return tracker(null, DIRECT.get(Partner.ID), null)
                .withPlatforms(asList(
                        defaultPlatform(MobPlatform.FALLBACK),
                        defaultPlatform(MobPlatform.ANDROID),
                        defaultPlatform(MobPlatform.I_OS)
                ));
    }

    public static Campaign doubleClickTracker() {
        return tracker(null, DOUBLECLICK.get(Partner.ID), null)
                .withPlatforms(emptyList())
                .withDoubleClickSrc("Src")
                .withDoubleClickCat("Cat")
                .withDoubleClickType("Type")
                .withDoubleClickToken("Token");
    }

    public static Campaign adwordsTrackerNoAppDeprecated() {
        return adwordsTrackerWithThreeMonthsAttrWindow()
                .withAdwordsConversionId(ADWORDS_CONVERSION_ID)
                .withAdwordsConversionLabel(ADWORDS_CONVERSION_LABEL)
                .withAdwordsLinkId(null);
    }

    public static Campaign adwordsTrackerNoAppSemiNew() {
        return adwordsTrackerWithThreeMonthsAttrWindow()
                .withAdwordsConversionId(ADWORDS_CONVERSION_ID)
                .withAdwordsConversionLabel(ADWORDS_CONVERSION_LABEL)
                .withAdwordsLinkId(ADWORDS_LINK_ID);
    }

    public static Campaign adwordsTrackerNoAppWithNewPostback() {
        return adwordsTrackerWithThreeMonthsAttrWindow()
                .withPostbacks(Collections.singletonList(adwordsPostback()));
    }

    public static Campaign adwordsTrackerNoApp() {
        return adwordsTrackerWithThreeMonthsAttrWindow();
    }

    private static Campaign adwordsTrackerWithThreeMonthsAttrWindow() {
        return adwordsTracker(null, null, AdwordsConversionValues.linkId(ADWORDS_LINK_ID))
                .withStrictAttributionWindow(StrictAttributionWindow.NINETY_DAYS);
    }

    public static Campaign adwordsTracker(Long appId, Long targetUrlId, AdwordsConversionValues conversion) {
        return adwordsTracker(appId, targetUrlId,
                conversion.getConversionId(), conversion.getConversionLabel(), conversion.getLinkId());
    }

    private static Campaign adwordsTracker(Long appId, Long targetUrlId,
                                           String conversionId, String conversionLabel, String linkId) {
        return tracker(appId, ADWORDS.get(Partner.ID), targetUrlId)
                .withStrictAttributionWindow(StrictAttributionWindow.THIRTY_DAYS)
                .withAdwordsConversionId(conversionId)
                .withAdwordsConversionLabel(conversionLabel)
                .withAdwordsLinkId(linkId);
    }

    public static Campaign defaultTrackerWithThreeMonthsAttrWindow() {
        return defaultTracker()
                .withStrictAttributionWindow(StrictAttributionWindow.NINETY_DAYS);
    }

    public static Campaign doubleClickTrackerWithPlatform() {
        return doubleClickTracker()
                .withPlatforms(singletonList(new CampaignPlatform().withName(MobPlatform.ANDROID)));
    }

    public static Campaign doubleClickTrackerWithFingerprintWindow() {
        return doubleClickTracker()
                .withFingerprintAttributionWindow(FingerprintAttributionWindow.ONE_DAY);
    }

    public static Campaign doubleClickTrackerWithEmptyCat() {
        return doubleClickTracker()
                .withDoubleClickCat(null);
    }

    public static Campaign tracker(Long appId, Long partnerId, Long targetUrlId) {
        CampaignPlatform platform = new CampaignPlatform()
                .withName(MobPlatform.ANDROID)
                .withTargetUrlId(targetUrlId);
        return new Campaign()
                .withApiKey(appId)
                .withPartnerId(partnerId)
                .withPlatforms(singletonList(platform))
                .withName(getTrackerName())
                .withReattributionEnabled(false)
                .withFingerprintAttributionWindow(FingerprintAttributionWindow.NONE)
                .withStrictAttributionWindow(StrictAttributionWindow.ONE_DAY)
                .withSource(CampaignSource.APPMETRICA);
    }

    public static TrackingPartner defaultPartner() {
        return new TrackingPartner()
                .withName(getPartnerName())
                .withWebsiteUrl("http://example.com");
    }

    public static TrackingPartner copy(TrackingPartner other) {
        return new TrackingPartner()
                .withId(other.getId())
                .withName(other.getName())
                .withOwnership(other.getOwnership())
                .withIconUrl(other.getIconUrl())
                .withCampaignsCount(other.getCampaignsCount())
                .withType(other.getType())
                .withWebsiteUrl(other.getWebsiteUrl());
    }

    public static PostbackTemplate defaultPostbackTemplate() {
        return new PostbackTemplate()
                .withTitle(getPostbackTemplateName())
                .withUrl(getPostbackTemplateUrl())
                .withMethod(PostbackMethod.GET)
                .withHeaders(ImmutableList.of())
                .withMandatory(false)
                .withKind(PostbackKind.CPI);
    }

    public static TrackingPartnerMacros defaultTrackingMacros() {
        return new TrackingPartnerMacros()
                .withUrlParam(getString(RANDOM_STRING_LENGTH))
                .withMacro(getString(RANDOM_STRING_LENGTH));
    }

    public static TrackingPartnerMacros copy(TrackingPartnerMacros other) {
        return new TrackingPartnerMacros()
                .withId(other.getId())
                .withPartnerId(other.getPartnerId())
                .withUrlParam(other.getUrlParam())
                .withMacro(other.getMacro());
    }

    public static TestDevice someTestDevice() {
        return testDevice(REATTRIBUTION, GOOGLE_AID);
    }

    public static TestDevice testDevice(TestDevicePurpose purpose, TestDeviceType type) {
        return new TestDevice()
                .withName(getTestDeviceName())
                .withDeviceId(getTestDeviceId())
                .withPurpose(purpose)
                .withType(type);
    }

    public static AdwordsConversionValues adwordsConversion() {
        return AdwordsConversionValues.linkId(ADWORDS_LINK_ID);
    }

    public static AdwordsConversionValues adwordsConversionSemiNew() {
        return AdwordsConversionValues.semiNew(ADWORDS_CONVERSION_ID, ADWORDS_CONVERSION_LABEL, ADWORDS_LINK_ID);
    }

    public static AdwordsConversionValues adwordsConversionDeprecated() {
        return AdwordsConversionValues.deprecated(ADWORDS_CONVERSION_ID, ADWORDS_CONVERSION_LABEL);
    }

    public static AdwordsConversionValues randomAdwordsConversionDeprecated() {
        return AdwordsConversionValues.deprecated(
                getString(RANDOM_STRING_LENGTH),
                getString(RANDOM_STRING_LENGTH));
    }

    public static AdwordsConversionValues randomAdwordsConversionSemiNew() {
        return AdwordsConversionValues.semiNew(
                getString(RANDOM_STRING_LENGTH),
                getString(RANDOM_STRING_LENGTH),
                getString(RANDOM_STRING_LENGTH));
    }

    public static AdwordsConversionValues randomAdwordsConversion() {
        return AdwordsConversionValues.linkId(getString(RANDOM_STRING_LENGTH));
    }

    public static Campaign trackerWithEcomPostback() {
        return tracker(null, ZORKA.get(Partner.ID), null)
                .withPostbacks(singletonList(
                        new Postback()
                                .withKind(PostbackKind.CPA)
                                .withSingle(false)
                                .withUrl(defaultPostbackUrl())
                                .withAttributionWindow(PostbackAttributionWindow.EIGHT_DAYS)
                                .withEventName(null)
                                .withEventType(AppEventType.ECOMMERCE)
                                .withEventSubtype("purchase")
                ));
    }

    public static Campaign trackerWithRevenuePostback() {
        return tracker(null, ZORKA.get(Partner.ID), null)
                .withPostbacks(singletonList(
                        new Postback()
                                .withKind(PostbackKind.CPA)
                                .withSingle(false)
                                .withUrl(defaultPostbackUrl())
                                .withAttributionWindow(PostbackAttributionWindow.EIGHT_DAYS)
                                .withEventName(null)
                                .withEventType(AppEventType.EVENT_REVENUE)
                ));
    }

    public static Campaign trackerWithPostPostback() {
        return tracker(null, ZORKA.get(Partner.ID), null)
                .withPostbacks(singletonList(postPostback()));
    }

    public static Campaign trackerWithOmniPostback() {
        return tracker(null, ZORKA.get(Partner.ID), null)
                .withPostbacks(singletonList(omniPostback()));
    }

    public static Campaign trackerWithRandomOmniPostback(long partnerId) {
        return tracker(null, partnerId, null)
                .withPostbacks(singletonList(randomOmniPostback()));
    }

    public static Postback tiktokPostback() {
        return defaultPostback()
                .withMethod(PostbackMethod.POST)
                .withUrl("https://analytics.tiktok.com/api/v1/track")
                .withBody("{\"context\":{\"app\":{}}}")
                .withMandatory(true);
    }

    public static Postback defaultPostback() {
        return new Postback()
                .withKind(PostbackKind.CPI)
                .withSingle(false)
                .withUrl(randomUrlAddress())
                .withMethod(PostbackMethod.GET)
                .withHeaders(emptyList())
                .withAttributionWindow(PostbackAttributionWindow.EIGHT_DAYS);
    }

    public static Postback oldPostback() {
        return defaultPostback()
                .withMethod(null)
                .withHeaders(null);
    }

    public static Postback postPostback() {
        return defaultPostback()
                .withUrl(defaultPostbackUrl())
                .withMethod(PostbackMethod.POST)
                .withHeaders(postPostbackHeaders())
                .withBody(postPostbackBody());
    }

    public static Postback omniPostback() {
        return new Postback()
                .withKind(PostbackKind.CPI)
                .withUrl(defaultPostbackUrl())
                .withMethod(PostbackMethod.GET)
                .withHeaders(emptyList())
                .withOmni(true);
    }

    public static Postback randomOmniPostback() {
        return new Postback()
                .withKind(PostbackKind.CPA)
                .withEventType(EVENT_CLIENT)
                .withEventName(randomAlphanumeric(10))
                .withUrl(defaultPostbackUrl())
                .withMethod(PostbackMethod.GET)
                .withHeaders(emptyList())
                .withOmni(true);
    }

    public static String defaultPostbackUrl() {
        return "http://example.comvcFbzclRFr";
    }

    public static List<PostbackHeader> postPostbackHeaders() {
        return singletonList(new PostbackHeader().withName("Authorization").withValue("x"));
    }

    public static String postPostbackBody() {
        return "{\"app\": 1}";
    }

    public static Postback adwordsPostback() {
        return new Postback()
                .withKind(PostbackKind.CPI)
                .withSingle(false)
                .withUrl("https://www.googleadservices.com/pagead/conversion/app/1.0?" +
                        "link_id={adwords_link_id}" +
                        "&app_event_type=custom" +
                        "&lat={limit_ad_tracking}" +
                        "&app_version={app_version_name}" +
                        "&os_version={os_version}" +
                        "&sdk_version={app_version_name}" +
                        "&timestamp={conversion_timestamp}" +
                        "&rdid={ios_ifa}{google_aid}" +
                        "&id_type=advertisingid")
                .withAttributionWindow(PostbackAttributionWindow.EIGHT_DAYS);
    }

    public static Postback mandatoryPostback() {
        return new Postback()
                .withKind(PostbackKind.CPI)
                .withSingle(false)
                .withUrl(randomUrlAddress())
                .withAttributionWindow(PostbackAttributionWindow.EIGHT_DAYS)
                .withMandatory(true);
    }

    public static String anotherPostbackUrl() {
        return "https://ya.ru";
    }

    public static ProfileCustomAttribute defaultCustomAttribute(ProfileAttributeType type) {
        return new ProfileCustomAttribute()
                .withName(getProfileAttributeName())
                .withType(type)
                .withStatus(ProfileStatus.ACTIVE);
    }

    public static String defaultSegmentParams(String paramValue) {
        return "{" +
                "\"filters\": [" +
                "    {" +
                "      \"id\": \"userAppId\"," +
                "      \"data\": {" +
                "        \"inverted\": false," +
                "        \"values\": [" +
                "          {" +
                "            \"operator\": \"==\"," +
                "            \"value\": \"" + paramValue + "\"" +
                "          }" +
                "        ]" +
                "      }" +
                "    }" +
                "  ]" +
                "}";
    }

    public static String defaultSegmentParams() {
        return defaultSegmentParams("ru.yandex.metro");
    }

    public static String defaultSegmentExpression(String paramValue) {
        return "exists ym:d:device with (appID=='" + paramValue + "')";
    }

    public static String defaultSegmentExpression() {
        return defaultSegmentExpression("ru.yandex.metro");
    }

    public static MobSegment defaultSegment() {
        return new MobSegment()
                .withName(getTestSegmentName())
                .withParams(defaultSegmentParams());
    }

    public static MobSegment copy(MobSegment other) {
        return new MobSegment()
                .withSegmentId(other.getSegmentId())
                .withApiKey(other.getApiKey())
                .withName(other.getName())
                .withParams(other.getParams())
                .withExpression(other.getExpression());
    }

    public static Funnel defaultFunnel() {
        return new Funnel()
                .withName(getTestFunnelName())
                .withFrontendPattern("params")
                .withComment("comment")
                .withPatternType(FunnelPatternType.USER)
                .withPattern("cond(ym:uft, isAnyEvent=='yes')");
    }

    public static Funnel editFunnel(Funnel addedFunnel) {
        return new Cloner().deepClone(addedFunnel)
                .withFrontendPattern("update")
                .withComment("update comment")
                .withPatternType(FunnelPatternType.SESSION)
                .withPattern("cond(ym:sft, isAnyEvent=='yes')");
    }

    public static CloudAuthKey editorCloudAuthKey() {
        return new CloudAuthKey()
                .withName("Test key " + randomAlphanumeric(10))
                .withFolderId("b1goohiheml0c9glafkh")
                .withServiceAccountId("ajecaakcctrl68k0trnj")
                .withPublicKeyId("ajer9l725dtb43cl1576")
                .withPrivateKey(getYcEditorPrivateKey());
    }

    public static CloudAuthKey viewerCloudAuthKey() {
        return new CloudAuthKey()
                .withName("Test key " + randomAlphanumeric(10))
                .withFolderId("b1goohiheml0c9glafkh")
                .withServiceAccountId("aje0thp9hesjfgvb2g7k")
                .withPublicKeyId("aje980lvql191jufvssr")
                .withPrivateKey(getYcViewerPrivateKey());
    }

    public static CloudExport defaultCloudExport() {
        return new CloudExport()
                .withServiceAccountId(CLOUD_VALID_SERVICE_ACCOUNT)
                .withClusterId(CLOUD_ONE_NODE_SHARD_CLUSTER)
                .withMetaTableName(CLIENT_EVENTS_TABLE)
                .withClickhouseTableName(CLIENT_EVENTS_TABLE + "_" + randomAlphanumeric(10))
                .withFields(asList(
                        "device_locale",
                        "device_model",
                        "app_package_name",
                        "city",
                        "device_type",
                        "event_json",
                        "event_timestamp",
                        "mcc",
                        "appmetrica_device_id",
                        "device_manufacturer",
                        "event_datetime",
                        "event_date",
                        "ios_ifv",
                        "event_receive_datetime",
                        "mnc",
                        "connection_type",
                        "os_version",
                        "ios_ifa",
                        "application_id",
                        "operator_name",
                        "google_aid",
                        "country_iso_code",
                        "event_receive_timestamp",
                        "os_name",
                        "event_name",
                        "android_id",
                        "app_version_name"
                ))
                .withType(CloudExportType.ONE_TIME)
                .withFromDate(LocalDate.now().format(ISO_LOCAL_DATE))
                .withToDate(LocalDate.now().minusDays(1).format(ISO_LOCAL_DATE));
    }

    public static CrashAlertSettingsSummary defaultCrashAlertSettingsSummary() {
        return new CrashAlertSettingsSummary()
                .withCrashAlertSettings(new CrashAlertSettings()
                        .withEmail(getNotificationEmail()));
    }

    public static CrashAlertSettingsSummary defaultCrashAlertSettingsSummary(String email) {
        return new CrashAlertSettingsSummary()
                .withCrashAlertSettings(new CrashAlertSettings()
                        .withEmail(email));
    }

    public static CrashAlertSettingsSummary defaultCrashOpenAlertSettingsSummary(List<AppEventType> eventTypes) {
        return new CrashAlertSettingsSummary()
                .withCrashAlertSettings(new CrashAlertSettings()
                        .withEmail(getNotificationEmail()))
                .withOpenCrashGroupAlertEventTypes(eventTypes);
    }

    public static CrashAlertSettingsSummary defaultCrashVelocityAlertSettingsSummary(List<VelocityAlertConfig> configs) {
        return new CrashAlertSettingsSummary()
                .withCrashAlertSettings(new CrashAlertSettings()
                        .withEmail(getNotificationEmail()))
                .withVelocityAlertConfigs(configs);
    }

    public static CrashAlertSettingsSummary defaultFullAlertSettingsSummary() {
        return new CrashAlertSettingsSummary()
                .withCrashAlertSettings(new CrashAlertSettings()
                        .withEmail(getNotificationEmail()))
                .withOpenCrashGroupAlertEventTypes(asList(EVENT_PROTOBUF_CRASH, EVENT_PROTOBUF_ERROR))
                .withVelocityAlertConfigs(asList(
                        velocityAlertConfig(EVENT_PROTOBUF_CRASH, VelocityAlertType.TOTAL, 1000),
                        velocityAlertConfig(EVENT_PROTOBUF_ERROR, VelocityAlertType.TOTAL, 1000),
                        velocityAlertConfig(EVENT_PROTOBUF_CRASH, VelocityAlertType.PARTICULAR_GROUP, 100),
                        velocityAlertConfig(EVENT_PROTOBUF_ERROR, VelocityAlertType.PARTICULAR_GROUP, 100)));
    }

    public static VelocityAlertConfig velocityAlertConfig(AppEventType eventType,
                                                          VelocityAlertType alertType,
                                                          long rateThresholdInMicro) {
        return new VelocityAlertConfig()
                .withEventType(eventType)
                .withVelocityAlertType(alertType)
                .withRateThresholdInMicro(rateThresholdInMicro);
    }

    public static SKAdCVConfig defaultSKAdCVNotConfiguredConfig() {
        return new SKAdCVConfig().withModelType(NOT_CONFIGURED);
    }

    public static SKAdCVConfig defaultSKAdCVRevenueConfig() {
        return new SKAdCVConfig()
                .withModelType(REVENUE)
                .withBundleIds(ImmutableList.of(getBundleId()))
                .withRevenueModel(new SKAdCVRevenueModel()
                        .withEventType(EVENT_REVENUE)
                        .withStepSize(3.0)
                        .withCurrency("RUB"))
                .withMaxMeasurementTime(new SKAdMeasurementTime().withTime(2L).withUnit(SKAdMeasurementTimeUnit.DAYS));
    }

    public static SKAdCVConfig defaultSKAdCVEngagementConfig() {
        return new SKAdCVConfig()
                .withModelType(ENGAGEMENT)
                .withBundleIds(ImmutableList.of(getBundleId()))
                .withEngagementModel(new SKAdCVEngagementModel()
                        .withEventType(EVENT_REVENUE)
                        .withStepSize(3L))
                .withMaxMeasurementTime(new SKAdMeasurementTime().withTime(2L).withUnit(SKAdMeasurementTimeUnit.DAYS));
    }

    public static SKAdCVConfig defaultSKAdCVConversionConfig() {
        return new SKAdCVConfig()
                .withModelType(CONVERSION)
                .withBundleIds(ImmutableList.of(getBundleId()))
                .withConversionModel(new SKAdCVConversionModel().withEvents(singletonList(
                        new SKAdCVConversionModelEvent().withEventType(EVENT_CLIENT).withEventName("a"))))
                .withMaxMeasurementTime(new SKAdMeasurementTime().withTime(2L).withUnit(SKAdMeasurementTimeUnit.DAYS));
    }

    public static class GrantCreator {
        private final String login;

        public static GrantCreator forUser(User user) {
            return forLogin(user.get(LOGIN));
        }

        private static GrantCreator forLogin(String login) {
            return new GrantCreator(login);
        }

        private GrantCreator(String login) {
            this.login = login;
        }

        public MobmetGrantE defaultAgencyGrant() {
            return getAgencyViewGrantToMultiplePartnersAndEvents();
        }

        public MobmetGrantE agencyEditGrant() {
            return getAgencyEditGrantToMultiplePartners();
        }

        public MobmetGrantE getAgencyEditGrantToMultiplePartners() {
            return grant(GrantType.AGENCY_EDIT, ZORKA, DIRECT);
        }

        public MobmetGrantE agencyViewGrant() {
            return getAgencyViewGrantToMultiplePartnersAndEvents();
        }

        public MobmetGrantE getAgencyViewGrantToMultiplePartnersAndEvents() {
            return grant(GrantType.AGENCY_VIEW, ZORKA, DIRECT)
                    .withEventLabels(ImmutableList.of(eventLabel(1), eventLabel(2)));
        }

        public MobmetGrantE grant(GrantType type, Partner... partners) {
            return new MobmetGrantE()
                    .withPerm(type)
                    .withComment("")
                    .withUserLogin(login)
                    .withPartners(Stream.of(partners).map(p -> p.get(Partner.ID)).collect(Collectors.toList()));
        }
    }

    public static class PushCredentialsCreator {

        public static AndroidUpdateParameters getValidAndroidCredentials() {
            return new AndroidUpdateParameters(TestDataSecrets.getPassword("PushSampleAndroidAuthKey"));
        }

        public static AndroidUpdateParameters getInvalidAndroidCredentials() {
            return new AndroidUpdateParameters("ABC");
        }

        public static WinUpdateParameters getValidWinCredentials() {
            return new WinUpdateParameters(
                    "ms-app://s-1-15-2-3221435482-4103795870-3507741889-456717974-3487736137-4242306684-1357272952",
                    TestDataSecrets.getPassword("PushSampleWinSecretKey"));
        }

        public static WinUpdateParameters getInvalidWinCredentials() {
            return new WinUpdateParameters("ABC", "BCD");
        }

        public static HuaweiUpdateParameters getValidHuaweiCredentials() {
            return new HuaweiUpdateParameters(
                    "101625753",
                    TestDataSecrets.getPassword("PushSampleHmsClientSecret"));
        }

        public static HuaweiUpdateParameters getInvalidHuaweiCredentials() {
            return new HuaweiUpdateParameters("12345", "AAA");
        }

        public static AppleCredentialsInfo getAppleProdCredentials() {
            return new AppleCredentialsInfo(
                    loadCertFile("YandexMetricaPushSampleProdAPNs.p12"),
                    TestDataSecrets.getPassword("PushSampleApnsProdPassword"),
                    "production");
        }

        public static AppleCredentialsInfo getDevAppleCredentialsForDev() {
            return new AppleCredentialsInfo(
                    loadCertFile("YandexMetricaPushSampleDevAPNs.p12"),
                    TestDataSecrets.getPassword("PushSampleApnsDevPassword"),
                    "development");
        }

        public static AppleCredentialsInfo getDevAppleCredentialsForProd() {
            return new AppleCredentialsInfo(
                    loadCertFile("YandexMetricaPushSampleDevAPNs.p12"),
                    TestDataSecrets.getPassword("PushSampleApnsDevPassword"),
                    "production");
        }

        public static AppleCredentialsInfo getBadPassAppleCredentials() {
            return new AppleCredentialsInfo(
                    loadCertFile("YandexMetricaPushSampleProdAPNs.p12"),
                    "wrong_password",
                    "production");
        }

        public static AppleCredentialsInfo getRevokedAppleCredentials() {
            return new AppleCredentialsInfo(
                    loadCertFile("YandexMetricaPushSampleRevokedProdAPNs.p12"),
                    "wrong_password",
                    "production");
        }

        public static AppleCredentialsInfo getExpiredAppleCredentials() {
            return new AppleCredentialsInfo(
                    loadCertFile("YandexMetricaPushSampleExpiredProdAPNs.p12"),
                    "yandexmetrica322",
                    "production");
        }

        public static PushCredentialsSummary emptySummary() {
            return new PushCredentialsSummary();
        }

        private static File loadCertFile(String cert) {
            URL certUrl = TestData.class.getResource("push/credentials/" + cert);
            try {
                return new File(certUrl.toURI());
            } catch (URISyntaxException ex) {
                throw new AppMetricaException(ex);
            }
        }

        public static String mask(String str) {
            if (str.length() < 4) {
                throw new IllegalArgumentException("Test string size should be greater than 4");
            }
            int len = str.length();
            return str.substring(0, 2) + StringUtils.repeat("*", len - 4) + str.substring(len - 2, len);
        }
    }

    public static class CrashCreator {
        public static byte[] loadSymbolsFileContent(String fileName) {
            URL symbolsUrl = TestData.class.getResource("crash/symbols/" + fileName);
            try {
                return IOUtils.toByteArray(symbolsUrl.toURI());
            } catch (Exception ex) {
                throw new AppMetricaException(ex);
            }
        }
    }

    public static class RevenueCreator {
        public static RevenueAppStoreCredentials mask(RevenueAppStoreCredentials credentials) {
            return new RevenueAppStoreCredentials()
                    .withVerificationEnabled(credentials.getVerificationEnabled())
                    .withSharedSecret(mask(credentials.getSharedSecret()));
        }

        public static RevenueGooglePlayCredentials mask(RevenueGooglePlayCredentials credentials) {
            return new RevenueGooglePlayCredentials()
                    .withVerificationEnabled(credentials.getVerificationEnabled())
                    .withPublicKey(mask(credentials.getPublicKey()));
        }

        public static String mask(String str) {
            if (str == null) {
                return null;
            }
            return StringUtils.repeat("*", 32);
        }
    }

    public static class TimeZoneInfo {

        private final String name;
        private final long offset;

        public static TimeZoneInfo getSingaporeTimeZone() {
            return new TimeZoneInfo("Asia/Singapore");
        }

        public static TimeZoneInfo getSamaraTimeZone() {
            return new TimeZoneInfo("Europe/Samara");
        }

        private TimeZoneInfo(String name) {
            this.name = name;
            this.offset = DateTimeZone.forID(name).getOffset(null) / 1000;
        }

        public String getName() {
            return name;
        }

        public long getOffset() {
            return offset;
        }
    }

    public static TableReportParameters createSkadReportDefaultParameters(long appId) {
        return new TableReportParameters()
                .withDimension("ym:sk:adNetworkName")
                .withMetric("ym:sk:installations")
                .withId(appId)
                .withAccuracy("high")
                .withDate1(apiProperties().getDefaultStartDate())
                .withDate2(apiProperties().getDefaultEndDate())
                .withLimit(10)
                .withLang("ru")
                .withRequestDomain("com");
    }

    // endregion
}
