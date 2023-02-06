package ru.yandex.autotests.metrika.tests.ft.management.summaryreport;

import java.util.List;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportSettings;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;

@Stories(Requirements.Story.Management.SUMMARY_REPORT)
@Title("Проверка выбранных метрик в еженедельных отчетах по умолчанию")
@RunWith(Parameterized.class)
public class SummaryReportDefaultSettingsTest extends SummaryReportSettingsTestBase {

    @Parameterized.Parameter
    public CounterFull counter;

    private long counterId;

    @Parameterized.Parameters
    public static List<Object[]> createParameters() {
        return asList(new Object[][]{
                {getDefaultCounter()},
                {getDefaultCounter().withFeatures(ImmutableList.of(Feature.VACUUM))},
                {getDefaultCounter().withFeatures(ImmutableList.of(Feature.VACUUM, Feature.ECOMMERCE))},
        });
    }

    @Before
    public void setup() {
        counterId = USER.onManagementSteps().onCountersSteps().addCounterAndExpectSuccess(
                counter
        ).getId();
    }

    @Test
    public void testDefaultMetrics() {
        SummaryReportSettings settings = USER.onManagementSteps().onSummaryReportSteps().getSettingsAndExpectSuccess(counterId);
        validateSettings(settings);
    }

    @After
    public void cleanUp() {
        USER.onManagementSteps().onCountersSteps().deleteCounterAndExpectSuccess(counterId);
    }

}
