package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax.user;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.filters.Expression;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SHATURA_COM;
import static ru.yandex.autotests.metrika.errors.ReportError.*;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.filters.Term.metric;
import static ru.yandex.autotests.metrika.filters.user.User.cond;
import static ru.yandex.autotests.metrika.filters.user.User.user;

/**
 * Created by konkov on 25.06.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({
        Requirements.Story.Report.Type.TABLE,
        Requirements.Story.Report.Parameter.FILTERS,
        Requirements.Story.USER_CENTRIC
})
@Title("Фильтры: user-centric, негативные тесты")
@RunWith(Parameterized.class)
public class FilterSyntaxUserNegativeTest {

    private static UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = SHATURA_COM;
    private static final String DIMENSION = "ym:s:browser";
    private static final String METRIC = "ym:s:users";
    private static final String START_DATE = "2014-01-01";
    private static final String END_DATE = "2014-01-02";
    private static final int MAXIMUM_ALLOWED_COND = 32;
    private static final int MAXIMUM_ALLOWED_DIMENSIONS = 20;
    private static final int MAXIMUM_ALLOWED_TERMS = 20;
    private static final List<String> DIMENSIONS = asList(
            "ym:s:startURLPath",
            "ym:s:startURLPathLevel1",
            "ym:s:startURLPathLevel2",
            "ym:s:startURLPathLevel3",
            "ym:s:startURLPathLevel4",
            "ym:s:startURLPathLevel5",
            "ym:s:endURLPath",
            "ym:s:endURLPathLevel1",
            "ym:s:endURLPathLevel2",
            "ym:s:endURLPathLevel3",
            "ym:s:endURLPathLevel4",
            "ym:s:endURLPathLevel5",
            "ym:s:visitYear",
            "ym:s:visitMonth",
            "ym:s:visitDayOfMonth",
            "ym:s:firstVisitYear",
            "ym:s:firstVisitMonth",
            "ym:s:firstVisitDayOfMonth",
            "ym:s:totalVisits",
            "ym:s:pageViews",
            "ym:s:visitDuration",
            "ym:s:visits"
    );

    @Parameter(0)
    public Expression filter;

    @Parameter(1)
    public IExpectedError error;

    @Parameters(name = "{0} : {1}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                //Диапазон дат
                {user("today", "yesterday"), WRONG_TIME_INTERVAL},
                {user("2014-01-02", "2014-01-01"), WRONG_TIME_INTERVAL},
                {user("90daysAgo", "today"), INTERVAL_TOO_BIG},
                {user("2014-01-01", "2014-04-01"), INTERVAL_TOO_BIG},

                //ограничение на количество cond
                {user("2014-01-01", "2014-03-31", user.onFilterSteps().getConditionSequence(MAXIMUM_ALLOWED_COND + 1)),
                        TOO_MANY_CONDITIONS},

                //фильтр по метрике не допустим
                {user("2014-01-01", "2014-01-01", cond("ym:s", metric("ym:s:manPercentage").greaterThan(0))),
                        WRONG_FILTER},

                //лимиты на api filter входят в общие лимиты по условиям и метрикам/измерениям на фильтры
                {user("2014-01-01", "2014-01-01", cond("ym:s", dimension("ym:s:browser").equalTo(1)))
                        .and(user.onFilterSteps().getFilterExpressionWithConditions(
                        "ym:s:age", MAXIMUM_ALLOWED_TERMS)),
                        TOO_MANY_TERMS_IN_FILTERS},

                {user("2014-01-01", "2014-01-01", cond("ym:s", dimension("ym:s:browser").equalTo(1)))
                        .and(user.onFilterSteps().getFilterExpressionWithAttributes(
                        DIMENSIONS, MAXIMUM_ALLOWED_DIMENSIONS)),
                        TOO_MANY_ATTRIBUTES_IN_FILTERS},

                //sequence relation
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .next().cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google"))),
                        WRONG_FILTER},
                {user("2014-01-01", "2014-01-01", cond("ym:pv", dimension("ym:s:browser").equalTo(1))),
                        WRONG_FILTER},
                {user("2014-01-01", "2014-01-01", cond("ym:s", dimension("ym:pv:browser").equalTo(1))),
                        WRONG_FILTER},

                //некорректная регулярка
                {user("2014-01-01", "2014-01-01", cond("ym:pv", dimension("ym:pv:URL").matchRegEx("("))),
                        WRONG_FILTER},
                {user("2014-01-01", "2014-01-01", cond("ym:pv", dimension("ym:pv:URL").notMatchRegEx("("))),
                        WRONG_FILTER},
        });
    }

    @Test
    public void filterSyntaxUserNegativeTest() {
        user.onReportSteps().getTableReportAndExpectError(
                error,
                new TableReportParameters()
                        .withId(COUNTER.get(ID))
                        .withDimension(DIMENSION)
                        .withMetric(METRIC)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)
                        .withAccuracy("low")
                        .withFilters(filter == null ? null : filter.build()));
    }
}
