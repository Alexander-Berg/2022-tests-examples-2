package ru.yandex.autotests.metrika.tests.ft.management.summaryreport;

import jersey.repackaged.com.google.common.collect.Lists;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportSettings;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Collections.emptyList;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getGoal;

@Stories(Requirements.Story.Management.SUMMARY_REPORT)
@Title("Проверка выбранных метрик в еженедельных отчетах - негативные")
public class SummaryReportSettingsNegativeTest extends SummaryReportSettingsTestBase {
    private long counterId;
    private long goalId;
    private long deletedGoalId;

    @Before
    public void setup() {
        counterId = USER.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(getDefaultCounter()).getId();
        deletedGoalId = USER.onManagementSteps().onGoalsSteps().addGoal(counterId, getGoal()).getId();
        USER.onManagementSteps().onGoalsSteps().deleteGoal(counterId, deletedGoalId);
    }

    @Test
    public void testEmptySelectedMetrics() {
        USER.onManagementSteps().onSummaryReportSteps().editSettingsAndExpectError(emptyList(), emptyList(), counterId,
                ManagementError.MISSED_QUERY_PARAMETER);
    }

    @Test
    public void testDeletedGoal() {
        SummaryReportSettings settings = USER.onManagementSteps()
                .onSummaryReportSteps().getSettingsAndExpectSuccess(counterId);

        USER.onManagementSteps().onSummaryReportSteps()
                .editSettingsAndExpectError(
                        getMetricNames(settings.getSelectedMetrics()),
                        Lists.newArrayList(deletedGoalId),
                        counterId,
                        ManagementError.NOT_FOUND
                );
    }

    @After
    public void cleanup() {
        USER.onManagementSteps().onSummaryReportSteps().clearSettingsAndExpectSuccess(counterId);
        USER.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
