package ru.yandex.autotests.metrika.tests.ft.management.summaryreport;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportSettings;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.isEmptyString;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getGoal;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Stories(Requirements.Story.Management.SUMMARY_REPORT)
@Title("Проверка выбранных метрик в еженедельных отчетах")
@RunWith(Parameterized.class)
public class SummaryReportSelectSettingsTest extends SummaryReportSettingsTestBase {


    @Parameterized.Parameter
    public List<Feature> features;

    @Parameterized.Parameter(1)
    public int leapLength;

    @Parameterized.Parameter(2)
    public int createGoalsAmount;

    private long counterId;
    private List<GoalE> goals;

    @Parameterized.Parameters
    public static List<Object[]> createParameters() {
        return asList(new Object[][]{
                {ImmutableList.of(), 2, 0},
                {ImmutableList.of(Feature.ECOMMERCE), 3, 1},
                {ImmutableList.of(Feature.VACUUM, Feature.ECOMMERCE), 1, 3}
        });
    }

    @Before
    public void setup() {
        counterId = USER.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter().withFeatures(features)).getId();

        goals = new ArrayList<>();

        for (int i = 0; i < createGoalsAmount; ++i) {
            goals.add(USER.onManagementSteps().onGoalsSteps().addGoal(counterId, getGoal()));
        }
    }

    @Test
    public void testMetricsSelection() {
        SummaryReportSettings settings = USER.onManagementSteps().onSummaryReportSteps()
                .getSettingsAndExpectSuccess(counterId);
        assertThat("Доступные метрики не пусты", settings.getAvailableMetrics(), not(isEmptyString()));

        validateSettings(settings);
        List<String> selectedMetrics = selectMetrics(getMetricNames(settings.getAvailableMetrics()));


        SummaryReportSettings newSettings = USER.onManagementSteps().onSummaryReportSteps()
                .editSettingsAndExpectSuccess(selectedMetrics, goals.stream().map(GoalE::getId).collect(Collectors.toList()), counterId);
        validateSettings(newSettings);

        assertThat("Выбранные метрики совпали", getMetricNames(newSettings.getSelectedMetrics()), is(selectedMetrics));
    }

    private List<String> selectMetrics(List<String> availableMetrics) {
        List<String> result = new ArrayList<>();
        for (int i = 0; i < availableMetrics.size(); i += leapLength) {
            result.add(availableMetrics.get(i));
        }
        return result;
    }

    @After
    public void cleanup() {
        USER.onManagementSteps().onSummaryReportSteps().clearSettingsAndExpectSuccess(counterId);

        for (GoalE goal : goals) {
            USER.onManagementSteps().onGoalsSteps().deleteGoal(counterId, goal.getId());
        }

        USER.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }
}
