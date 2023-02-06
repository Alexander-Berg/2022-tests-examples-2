package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;
import java.util.List;

import com.google.gson.TypeAdapterFactory;

import ru.yandex.autotests.metrika.appmetrica.core.LowercaseEnumTypeAdapterFactory;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.matchers.CAV2DataMatcher;
import ru.yandex.autotests.metrika.appmetrica.matchers.PairResponseMatcher;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;
import ru.yandex.metrika.mobmet.model.events.EventsResponse;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSessionEvents;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSessionsList;

import static org.apache.commons.lang3.tuple.ImmutablePair.of;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.CADataMatcher.expectNotEmptyCA;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ReportDataMatcher.expectNotEmptyReport;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.areBothSuccessful;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.isSimilarErrorCode;

/**
 * Created by konkov on 04.05.2016.
 */
public class UserSteps extends BaseUserSteps {

    private final MetadataSteps metadataSteps;
    private final ReportSteps reportSteps;
    private final ReportSKAdNetworkSteps reportSKAdNetworkSteps;
    private final OrganizationSteps organizationSteps;
    private final OrganizationStructureSteps organizationStructureSteps;
    private final ApplicationSteps applicationSteps;
    private final AdminSteps adminSteps;
    private final LabelSteps labelSteps;
    private final PushCampaignSteps pushCampaignSteps;
    private final GrantSteps grantSteps;
    private final TrackerSteps trackerSteps;
    private final PartnerSteps partnerSteps;
    private final PostbackTemplateSteps postbackTemplateSteps;
    private final TrackingMacrosSteps trackingMacrosSteps;
    private final TestDeviceSteps testDevicesSteps;
    private final PushCredentialsSteps pushCredentialsSteps;
    private final CohortAnalysisSteps cohortAnalysisSteps;
    private final CohortAnalysisV2Steps cohortAnalysisV2Steps;
    private final TrafficSourcesSteps trafficSourcesSteps;
    private final SegmentsSteps segmentSteps;
    private final FunnelsSteps funnelsSteps;
    private final ProfileSteps profileSteps;
    private final EventsManagementSteps eventsManagementSteps;
    private final CommonSymbolsUploadSteps commonSymbolsUploadSteps;
    private final RevenueCurrenciesSteps revenueCurrenciesSteps;
    private final CrashGroupManagementSteps crashGroupManagementSteps;
    private final CrashAlertSettingsSteps crashAlertSettingsSteps;
    private final StackTraceReportSteps stackTraceReportSteps;
    private final RevenueCredentialsSteps revenueCredentialsSteps;
    private final RevenueSettingsSteps revenueSettingsSteps;
    private final CloudAuthKeysSteps cloudAuthKeysSteps;
    private final CloudExportsSteps cloudExportsSteps;
    private final CloudExportMetaSteps cloudExportMetaSteps;
    private final CloudClustersSteps cloudClustersSteps;
    private final SKAdConversionValueSteps skadConversionValueSteps;

    private UserSteps(Builder builder) {
        super(builder);

        metadataSteps = createWithParallelismControl(MetadataSteps.class, getBaseUrl(), getHttpClient());
        reportSteps = createWithParallelismControl(ReportSteps.class, getBaseUrl(), getHttpClient());
        reportSKAdNetworkSteps = createWithParallelismControl(ReportSKAdNetworkSteps.class, getBaseUrl(),
                getHttpClient());
        organizationSteps = createWithParallelismControl(OrganizationSteps.class, getBaseUrl(), getHttpClient());
        organizationStructureSteps = createWithParallelismControl(OrganizationStructureSteps.class, getBaseUrl(),
                getHttpClient());
        applicationSteps = createWithParallelismControl(ApplicationSteps.class, getBaseUrl(), getHttpClient());
        adminSteps = createWithParallelismControl(AdminSteps.class, getBaseUrl(), getHttpClient());
        labelSteps = createWithParallelismControl(LabelSteps.class, getBaseUrl(), getHttpClient());
        pushCampaignSteps = createWithParallelismControl(PushCampaignSteps.class, getBaseUrl(), getHttpClient());
        grantSteps = createWithParallelismControl(GrantSteps.class, getBaseUrl(), getHttpClient());
        trackerSteps = createWithParallelismControl(TrackerSteps.class, getBaseUrl(), getHttpClient());
        partnerSteps = createWithParallelismControl(PartnerSteps.class, getBaseUrl(), getHttpClient());
        postbackTemplateSteps = createWithParallelismControl(PostbackTemplateSteps.class, getBaseUrl(),
                getHttpClient());
        trackingMacrosSteps = createWithParallelismControl(TrackingMacrosSteps.class, getBaseUrl(), getHttpClient());
        testDevicesSteps = createWithParallelismControl(TestDeviceSteps.class, getBaseUrl(), getHttpClient());
        pushCredentialsSteps = createWithParallelismControl(PushCredentialsSteps.class, getBaseUrl(), getHttpClient());
        cohortAnalysisSteps = createWithParallelismControl(CohortAnalysisSteps.class, getBaseUrl(), getHttpClient());
        cohortAnalysisV2Steps = createWithParallelismControl(CohortAnalysisV2Steps.class, getBaseUrl(),
                getHttpClient());
        trafficSourcesSteps = createWithParallelismControl(TrafficSourcesSteps.class, getBaseUrl(), getHttpClient());
        segmentSteps = createWithParallelismControl(SegmentsSteps.class, getBaseUrl(), getHttpClient());
        funnelsSteps = createWithParallelismControl(FunnelsSteps.class, getBaseUrl(), getHttpClient());
        profileSteps = createWithParallelismControl(ProfileSteps.class, getBaseUrl(), getHttpClient());
        eventsManagementSteps = createWithParallelismControl(EventsManagementSteps.class, getBaseUrl(),
                getHttpClient());
        commonSymbolsUploadSteps = createWithParallelismControl(CommonSymbolsUploadSteps.class, getBaseUrl(),
                getHttpClient());
        revenueCurrenciesSteps = createWithParallelismControl(RevenueCurrenciesSteps.class, getBaseUrl(),
                getHttpClient());
        crashGroupManagementSteps = createWithParallelismControl(CrashGroupManagementSteps.class, getBaseUrl(),
                getHttpClient());
        crashAlertSettingsSteps = createWithParallelismControl(CrashAlertSettingsSteps.class, getBaseUrl(),
                getHttpClient());
        stackTraceReportSteps = createWithParallelismControl(StackTraceReportSteps.class, getBaseUrl(),
                getHttpClient());
        revenueCredentialsSteps = createWithParallelismControl(RevenueCredentialsSteps.class, getBaseUrl(),
                getHttpClient());
        revenueSettingsSteps = createWithParallelismControl(RevenueSettingsSteps.class, getBaseUrl(), getHttpClient());
        cloudAuthKeysSteps = createWithParallelismControl(CloudAuthKeysSteps.class, getBaseUrl(), getHttpClient());
        cloudExportsSteps = createWithParallelismControl(CloudExportsSteps.class, getBaseUrl(), getHttpClient());
        cloudExportMetaSteps = createWithParallelismControl(CloudExportMetaSteps.class, getBaseUrl(), getHttpClient());
        cloudClustersSteps = createWithParallelismControl(CloudClustersSteps.class, getBaseUrl(), getHttpClient());
        skadConversionValueSteps = createWithParallelismControl(SKAdConversionValueSteps.class, getBaseUrl(),
                getHttpClient());
    }

    public MetadataSteps onMetadataSteps() {
        return metadataSteps;
    }

    public ReportSteps onReportSteps() {
        return reportSteps;
    }

    public ReportSKAdNetworkSteps onReportSKAdNetworkSteps() {
        return reportSKAdNetworkSteps;
    }

    public ApplicationSteps onApplicationSteps() {
        return applicationSteps;
    }

    public AdminSteps onAdminSteps() {
        return adminSteps;
    }

    public LabelSteps onLabelSteps() {
        return labelSteps;
    }

    public GrantSteps onGrantSteps() {
        return grantSteps;
    }

    public PushCampaignSteps onPushCampaignSteps() {
        return pushCampaignSteps;
    }

    public PushCredentialsSteps onPushCredentialsSteps() {
        return pushCredentialsSteps;
    }

    public TrackerSteps onTrackerSteps() {
        return trackerSteps;
    }

    public PartnerSteps onPartnerSteps() {
        return partnerSteps;
    }

    public PostbackTemplateSteps onPostbackTemplateSteps() {
        return postbackTemplateSteps;
    }

    public TrackingMacrosSteps onTrackingMacrosSteps() {
        return trackingMacrosSteps;
    }

    public TestDeviceSteps onTestDevicesSteps() {
        return testDevicesSteps;
    }

    public CohortAnalysisSteps onCohortAnalysisSteps() {
        return cohortAnalysisSteps;
    }

    public CohortAnalysisV2Steps onCohortAnalysisV2Steps() {
        return cohortAnalysisV2Steps;
    }

    public TrafficSourcesSteps onTrafficSourceSteps() {
        return trafficSourcesSteps;
    }

    public SegmentsSteps onSegmentSteps() {
        return segmentSteps;
    }

    public FunnelsSteps onFunnelsSteps() {
        return funnelsSteps;
    }

    public ProfileSteps onProfileSteps() {
        return profileSteps;
    }

    public EventsManagementSteps onEventsManagementSteps() {
        return eventsManagementSteps;
    }

    public CommonSymbolsUploadSteps onCommonSymbolsUploadSteps() {
        return commonSymbolsUploadSteps;
    }

    public RevenueCurrenciesSteps onRevenueCurrenciesSteps() {
        return revenueCurrenciesSteps;
    }

    public CrashGroupManagementSteps onCrashGroupManagementSteps() {
        return crashGroupManagementSteps;
    }

    public CrashAlertSettingsSteps onCrashAlertSettingsSteps() {
        return crashAlertSettingsSteps;
    }

    public StackTraceReportSteps onStackTraceReportSteps() {
        return stackTraceReportSteps;
    }

    public RevenueCredentialsSteps onRevenueCredentialsSteps() {
        return revenueCredentialsSteps;
    }

    public RevenueSettingsSteps onRevenueSettingsSteps() {
        return revenueSettingsSteps;
    }

    public CloudAuthKeysSteps onCloudAuthKeysSteps() {
        return cloudAuthKeysSteps;
    }

    public CloudExportsSteps onCloudExportsSteps() {
        return cloudExportsSteps;
    }

    public CloudExportMetaSteps onCloudExportMetaSteps() {
        return cloudExportMetaSteps;
    }

    public CloudClustersSteps onCloudClustersSteps() {
        return cloudClustersSteps;
    }

    public SKAdConversionValueSteps onSKAdConversionValueSteps() {
        return skadConversionValueSteps;
    }

    public static UserSteps onTesting() {
        return onTesting(Users.SIMPLE_USER);
    }

    public static UserSteps onTesting(User user) {
        return new Builder()
                .withOauthToken(user)
                .withBaseUrl(AppMetricaApiProperties.apiProperties().getApiTesting())
                .build();
    }

    public static UserSteps onProductionWithToken(User user) {
        return new Builder()
                .withOauthToken(user)
                .withBaseUrl(AppMetricaApiProperties.apiProperties().getApiProduction())
                .build();
    }

    public static UserSteps onProductionWithUid(User user) {
        return new Builder()
                .withUidReal(user)
                .withBaseUrl(AppMetricaApiProperties.apiProperties().getApiProduction())
                .build();
    }

    public static Builder builder() {
        return new Builder();
    }

    public OrganizationSteps onOrganizationSteps() {
        return organizationSteps;
    }

    public OrganizationStructureSteps onOrganizationStructureSteps() {
        return organizationStructureSteps;
    }

    public static class Builder extends BaseBuilder {
        public Builder() {
            this.withTypeAdapterFactory(new LowercaseEnumTypeAdapterFactory());
        }

        @Override
        public Builder withBaseUrl(URL baseUrl) {
            super.withBaseUrl(baseUrl);
            return this;
        }

        @Override
        public Builder withUser(User user) {
            super.withUser(user);
            return this;
        }

        @Override
        public Builder withOauthToken(User user) {
            super.withOauthToken(user);
            return this;
        }

        @Override
        public Builder withUidReal(User user) {
            super.withUidReal(user);
            return this;
        }

        @Override
        public Builder withTypeAdapterFactory(TypeAdapterFactory typeAdapterFactory) {
            super.withTypeAdapterFactory(typeAdapterFactory);
            return this;
        }

        @Override
        public UserSteps build() {
            return new UserSteps(this);
        }
    }

    public static void assumeOnResponse(Object testingBean) {
        assumeThat("запрос был успешным", testingBean, expectSuccess());
        assumeThat("ответа содержит непустой отчет", testingBean, expectNotEmptyReport());
    }

    public static void assumeOnResponses(Object testingBean, Object referenceBean) {
        assumeThat("обе среды ответили одинаковым кодом", testingBean, isSimilarErrorCode(referenceBean));
        assumeThat("оба запроса были успешны", of(referenceBean, testingBean), areBothSuccessful());
        assumeThat("оба ответа содержат непустой отчет",
                of(referenceBean, testingBean),
                new PairResponseMatcher<>(expectNotEmptyReport(), expectNotEmptyReport()));
    }

    public static void assumeOnCaResponses(Object testingBean, Object referenceBean) {
        assumeThat("оба ответа содержат непустой отчет",
                of(referenceBean, testingBean),
                new PairResponseMatcher<>(expectNotEmptyCA(), expectNotEmptyCA()));
    }

    public static void assumeOnCaV2Responses(Object testingBean, Object referenceBean) {
        assumeThat("оба ответа содержат непустой отчет",
                of(referenceBean, testingBean),
                new PairResponseMatcher<>(CAV2DataMatcher.expectNotEmptyCA(), CAV2DataMatcher.expectNotEmptyCA()));
    }

    public static void assumeOnEvents(EventsResponse testingBean, EventsResponse referenceBean) {
        assumeThat("оба ответа содержат непустое множество событий",
                of(referenceBean.getEvents(), testingBean.getEvents()),
                new PairResponseMatcher<>(not(empty()), not(empty())));
    }

    public static void assumeOnSessions(ProfileSessionsList testingBean, ProfileSessionsList referenceBean) {
        assumeThat("оба ответа содержат непустой список сессий",
                of(referenceBean.getSessions(), testingBean.getSessions()),
                new PairResponseMatcher<>(not(empty()), not(empty())));
    }

    public static void assumeOnSessionEvents(List<ProfileSessionEvents> testingBean,
                                             List<ProfileSessionEvents> referenceBean) {
        assumeThat("оба ответа содержат непустой список цепочек событий",
                of(referenceBean, testingBean),
                new PairResponseMatcher<>(not(empty()), not(empty())));
    }
}
