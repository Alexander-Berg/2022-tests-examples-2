package ru.yandex.autotests.metrika.tests.ft.management.summaryreport;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;
import ru.yandex.metrika.api.management.client.external.summaryreport.SummaryReportSettings;

import static org.hamcrest.core.Is.is;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

public class SummaryReportSettingsTestBase {

    protected static final UserSteps USER = new UserSteps().withUser(Users.SIMPLE_USER);

    protected void validateSettings(SummaryReportSettings settings) {
        Set<String> availableMetrics = new HashSet<>(getMetricNames(settings.getAvailableMetrics()));
        Set<String> activeMetrics = new HashSet<>(getMetricNames(settings.getSelectedMetrics()));

        assertThat(
                "Набор выбранных метрик является подмножеством доступных",
                availableMetrics.containsAll(activeMetrics), is(true));
    }

    protected List<String> getMetricNames(List<MetricMetaExternal> metricMetaExternals) {
        return metricMetaExternals.stream().map(MetricMetaExternal::getDim).toList();
    }
}
