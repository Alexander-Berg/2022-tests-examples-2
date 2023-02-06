package ru.yandex.autotests.metrika.steps.management;

import java.util.ArrayList;
import java.util.List;

import com.google.common.base.Joiner;
import org.hamcrest.Matcher;

import ru.yandex.autotests.metrika.beans.schemes.InternalAdminSummaryreportFeatureMetricsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdSummaryreportSettingsDELETESchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdSummaryreportSettingsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.ManagementV1CounterCounterIdSummaryreportSettingsPUTSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportFeatureMetrics;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportSettings;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class SummaryReportManagementSteps extends MetrikaBaseSteps {
    private static final String SUMMARY_REPORT_SETTINGS_URL = "/management/v1/counter/%d/summaryreport/settings";
    private static final String SUMMARY_REPORT_FEATURE_METRICS_URL = "/internal/admin/summaryreport/feature/metrics";

    public SummaryReportSettings getSettingsAndExpectSuccess(Long counterId) {
        return getSettings(SUCCESS_MESSAGE, expectSuccess(), counterId);
    }

    public SummaryReportSettings editSettingsAndExpectSuccess(List<String> selectedMetrics, List<Long> goalIds, Long counterId) {
        return editSettings(SUCCESS_MESSAGE, expectSuccess(), selectedMetrics, goalIds, counterId);
    }

    public void editSettingsAndExpectError(List<String> selectedMetrics, List<Long> goalIds, Long counterId, IExpectedError error) {
        editSettings(ERROR_MESSAGE, expectError(error), selectedMetrics, goalIds, counterId);
    }

    public void clearSettingsAndExpectSuccess(Long counterId) {
        clearSettings(SUCCESS_MESSAGE, expectSuccess(), counterId);
    }

    public SummaryReportFeatureMetrics getFeatureMetricsAndExpectSuccess(String featureName) {
        return getFeatureMetrics(SUCCESS_MESSAGE, expectSuccess(), featureName);
    }

    private SummaryReportFeatureMetrics getFeatureMetrics(String message, Matcher matcher, String featureName) {
        InternalAdminSummaryreportFeatureMetricsGETSchema result = executeAsJson(
                getRequestBuilder(SUMMARY_REPORT_FEATURE_METRICS_URL).get(makeParameters()
                        .append("feature_name", featureName))
        ).readResponse(InternalAdminSummaryreportFeatureMetricsGETSchema.class);
        assertThat(message, result, matcher);

        return result.getFeatureMetrics();
    }

    private SummaryReportSettings editSettings(String message, Matcher matcher, List<String> selectedMetrics, List<Long> goalIds, Long counterId) {
        ManagementV1CounterCounterIdSummaryreportSettingsPUTSchema result = executeAsJson(
                getRequestBuilder(format(SUMMARY_REPORT_SETTINGS_URL, counterId))
                        .put(makeParameters()
                                .append("selected_metrics", Joiner.on(",").join(selectedMetrics))
                                .append("goal_ids", Joiner.on(",").join(goalIds))
                        )
        ).readResponse(ManagementV1CounterCounterIdSummaryreportSettingsPUTSchema.class);

        assertThat(message, result, matcher);

        return result.getSummaryReportSettings();
    }

    private SummaryReportSettings getSettings(String message, Matcher matcher, Long counterId) {
        ManagementV1CounterCounterIdSummaryreportSettingsGETSchema result = executeAsJson(
                getRequestBuilder(format(SUMMARY_REPORT_SETTINGS_URL, counterId)).get()
        ).readResponse(ManagementV1CounterCounterIdSummaryreportSettingsGETSchema.class);

        assertThat(message, result, matcher);

        return result.getSummaryReportSettings();
    }

    private void clearSettings(String message, Matcher matcher, Long counterId) {
        ManagementV1CounterCounterIdSummaryreportSettingsDELETESchema result =
                executeAsJson(getRequestBuilder(format(SUMMARY_REPORT_SETTINGS_URL, counterId))
                        .delete(new ArrayList<>()))
                        .readResponse(ManagementV1CounterCounterIdSummaryreportSettingsDELETESchema.class);

        assertThat(message, result, matcher);
    }
}
