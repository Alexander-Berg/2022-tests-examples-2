package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax;

import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.steps.UserSteps;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.addTextAttachment;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.changeTestCaseTitle;
import static ru.yandex.autotests.metrika.commons.text.UnicodeEscape.escapeUnicode;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;

/**
 * Created by konkov on 08.05.2015.
 */
public abstract class FilterSyntaxBaseTest {

    protected static final Counter COUNTER = CounterConstants.LITE_DATA;

    protected static UserSteps user;

    @Parameterized.Parameter(0)
    public String dimension;

    @Parameterized.Parameter(1)
    public String metric;

    @Parameterized.Parameter(2)
    public Expression filter;

    @BeforeClass
    public static void init() {
        user = new UserSteps().withDefaultAccuracy();
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
        user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withId(COUNTER.get(ID))
                        .withDimension(dimension)
                        .withMetric(metric)
                        .withAccuracy("low")
                        .withFilters(filter == null ? null : filter.build()));
    }
}
