package ru.yandex.autotests.metrika.steps.management;

import ru.yandex.autotests.metrika.data.common.handles.SegmentsPathFragment;
import ru.yandex.autotests.metrika.properties.MetrikaApiProperties;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;

/**
 * Created by proxeter on 24.07.2014.
 */
public class ManagementSteps extends MetrikaBaseSteps {

    public CountersSteps onCountersSteps() {
        return createStepsWithCommonSettings(CountersSteps.class);
    }

    public GoalsSteps onGoalsSteps() {
        return createStepsWithCommonSettings(GoalsSteps.class);
    }

    public FiltersSteps onFiltersSteps() {
        return createStepsWithCommonSettings(FiltersSteps.class);
    }

    public OperationsSteps onOperationsSteps() {
        return createStepsWithCommonSettings(OperationsSteps.class);
    }

    public LabelsSteps onLabelsSteps() {
        return createStepsWithCommonSettings(LabelsSteps.class);
    }

    public LogsApiSteps onLogsApiSteps() {
        return createStepsWithCommonSettings(LogsApiSteps.class);
    }

    public SegmentsSteps onSegmentsSteps() {
        return createStepsWithCommonSettings(SegmentsSteps.class)
                .withPathFragment(MetrikaApiProperties.getInstance().getApiSegmentsType());
    }

    public SegmentsSteps onInterfaceSegmentsSteps() {
        return createStepsWithCommonSettings(SegmentsSteps.class)
                .withPathFragment(SegmentsPathFragment.INTERFACE);
    }

    public SegmentsSteps onApiSegmentsSteps() {
        return createStepsWithCommonSettings(SegmentsSteps.class)
                .withPathFragment(SegmentsPathFragment.API);
    }

    public DelegatesSteps onDelegatesSteps() {
        return createStepsWithCommonSettings(DelegatesSteps.class);
    }

    public GrantsSteps onGrantsSteps() {
        return createStepsWithCommonSettings(GrantsSteps.class);
    }

    public GrantRequestsSteps onGrantRequestsSteps() {
        return createStepsWithCommonSettings(GrantRequestsSteps.class);
    }

    public ClientSteps onClientSteps() {
        return createStepsWithCommonSettings(ClientSteps.class);
    }

    public QuotasSteps onQuotasSteps() {
        return createStepsWithCommonSettings(QuotasSteps.class);
    }

    public UserParamsSteps onUserParamsSteps() {
        return createStepsWithCommonSettings(UserParamsSteps.class);
    }

    public NotificationsSteps onNotificationsSteps() {
        return createStepsWithCommonSettings(NotificationsSteps.class);
    }

    public OfflineConversionSteps onOfflineConversionSteps() {
        return createStepsWithCommonSettings(OfflineConversionSteps.class);
    }

    public ExpenseSteps onExpenseSteps() {
        return createStepsWithCommonSettings(ExpenseSteps.class);
    }

    public SubscriptionsSteps onSubscriptionsSteps() {
        return createStepsWithCommonSettings(SubscriptionsSteps.class);
    }

    public YclidConversionSteps onYclidConversionSteps() {
        return createStepsWithCommonSettings(YclidConversionSteps.class);
    }

    public ClientSettingsSteps onClientSettingsSteps() {
        return createStepsWithCommonSettings(ClientSettingsSteps.class);
    }

    public ChartAnnotationSteps onChartAnnotationSteps() {
        return createStepsWithCommonSettings(ChartAnnotationSteps.class);
    }

    public WebmasterLinkPublicSteps onWebmasterLinkPublicSteps() {
        return createStepsWithCommonSettings(WebmasterLinkPublicSteps.class);
    }

    public WebmasterLinkInternalSteps onWebmasterLinkInternalSteps() {
        return createStepsWithCommonSettings(WebmasterLinkInternalSteps.class);
    }

    public ReportOrderManagementSteps onReportOrderSteps() {
        return createStepsWithCommonSettings(ReportOrderManagementSteps.class);
    }

    public CurrencySteps onCurrencySteps() {
        return createStepsWithCommonSettings(CurrencySteps.class);
    }

    public QuotaMultiplierSteps onQuotaMultiplierSteps() {
        return createStepsWithCommonSettings(QuotaMultiplierSteps.class);
    }

    public AdsConnectorsSteps onAdsConnectorsSteps() {
        return createStepsWithCommonSettings(AdsConnectorsSteps.class);
    }

    public SummaryReportManagementSteps onSummaryReportSteps() {
        return createStepsWithCommonSettings(SummaryReportManagementSteps.class);
    }
}
