package ru.yandex.autotests.metrika.tests.ft.report.analytics.filters;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.data.analytics.v3.enums.AnalyticsSampleAccuracyEnum;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.analytics.v3.AnalyticsParameters;
import ru.yandex.autotests.metrika.data.report.v1.enums.ReportFilterType;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.steps.UserSteps;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.addTextAttachment;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.changeTestCaseTitle;
import static ru.yandex.autotests.metrika.commons.text.UnicodeEscape.escapeUnicode;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

/**
 * Created by sourx on 26.05.2016.
 */
public abstract class AnalyticsFilterSyntaxBaseTest {
    private final ReportFilterType REPORT_TYPE = ReportFilterType.ANALYTICS;

    protected static final Counter COUNTER = CounterConstants.LITE_DATA;
    protected static final String START_DATE = "14daysAgo";
    protected static final String END_DATE = "7daysAgo";

    protected static UserSteps user;

    @Parameterized.Parameter(0)
    public String dimension;

    @Parameterized.Parameter(1)
    public String metric;

    @Parameterized.Parameter(2)
    public Expression filter;

    @BeforeClass
    public static void init() {
        user = new UserSteps();
    }

    @Before
    public void setup() {
        String filterString = filter != null
                ? filter.toString()
                : metric;
        addTextAttachment("Фильтр", filterString);
        changeTestCaseTitle(format("filter=%s", escapeUnicode(filterString)));
    }

    @Test
    public void filterSyntaxTest() {
        user.onReportSteps().getAnalyticsReportAndExpectSuccess(
                new AnalyticsParameters()
                        .withIds(COUNTER.get(ID))
                        .withStartDate(START_DATE)
                        .withEndDate(END_DATE)
                        .withDimensions(dimension)
                        .withMetrics(metric)
                        .withSamplingLevel(AnalyticsSampleAccuracyEnum.DEFAULT)
                        .withFilters(filter == null ? null : filter.build(REPORT_TYPE))
                        .withStartIndex(1)
        );
    }
}
