package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table.syntax.user;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
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
import static ru.yandex.autotests.metrika.filters.Not.not;
import static ru.yandex.autotests.metrika.filters.Relation.*;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.filters.user.TimeSequenceRelation.*;
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
@Title("Фильтры: user-centric")
@RunWith(Parameterized.class)
public class FilterSyntaxUserTest {

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

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule(true);

    @Parameter
    public Expression filter;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        return asList(new Object[][]{
                //интервалы дат
                {user("yesterday", "today")},
                {user("2daysAgo", "yesterday")},
                //90 дней
                {user("89daysAgo", "today")},
                {user("2014-01-01", "2014-03-31")},

                //неймспейсы
                {user("2014-01-01", "2014-01-01", cond("ym:s", dimension("ym:s:browser").equalTo(1)))},
                {user("2014-01-01", "2014-01-01", cond("ym:pv", dimension("ym:pv:browser").equalTo(1)))},
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .any().cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},

                //несколько cond
                {user("2014-01-01", "2014-01-01", user.onFilterSteps().getConditionSequence(2))},

                //AND OR NOT внутри cond
                {user("2014-01-01", "2014-01-01", cond("ym:s",
                        dimension("ym:s:startURL").matchSubstring("yandex")
                                .and(dimension("ym:s:browser").equalTo(1))))},
                {user("2014-01-01", "2014-01-01", cond("ym:s",
                        dimension("ym:s:startURL").matchSubstring("yandex")
                                .or(dimension("ym:s:browser").equalTo(1))))},
                {user("2014-01-01", "2014-01-01", cond("ym:s",
                        dimension("ym:s:startURL").matchSubstring("yandex")
                                .and(not(dimension("ym:s:browser").equalTo(1)))))},

                //EXISTS ALL NONE
                {user("2014-01-01", "2014-01-01", cond("ym:s",
                        exists(dimension("ym:s:paramsLevel1").equalTo("client_id"))))},
                {user("2014-01-01", "2014-01-01", cond("ym:s",
                        all(dimension("ym:s:paramsLevel1").equalTo("client_id"))))},
                {user("2014-01-01", "2014-01-01", cond("ym:s",
                        none(dimension("ym:s:paramsLevel1").equalTo("client_id"))))},

                //измерение из множества
                {user("2014-01-01", "2014-01-01", cond("ym:s", dimension("ym:s:paramsLevel1").equalTo("client_id")))},

                //максимально допустимое количество условий
                {user("2014-01-01", "2014-01-01", cond("ym:s", dimension("ym:s:browser").equalTo(1)))
                        .and(user.onFilterSteps().getFilterExpressionWithConditions(
                        "ym:s:age", MAXIMUM_ALLOWED_TERMS - 1))},

                //максимально допустимое количество измерений
                {user("2014-01-01", "2014-01-01", cond("ym:s", dimension("ym:s:browser").equalTo(1)))
                        .and(user.onFilterSteps().getFilterExpressionWithAttributes(
                        DIMENSIONS, MAXIMUM_ALLOWED_DIMENSIONS - 1))},

                {user("2014-01-01", "2014-01-01", user.onFilterSteps().getConditionSequence(MAXIMUM_ALLOWED_COND))},

                //sequence relations
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},
                {user("2014-01-01", "2014-01-01",
                        cond("ym:pv", dimension("ym:pv:URL").matchSubstring("yandex"))
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},

                //все отношения
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .time(greaterThan(1).sec())
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .time(lessThan(1).sec())
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .time(greaterThanOrEqual(1).sec())
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .time(lessThanOrEqual(1).sec())
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},

                //все единицы измерения
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .time(greaterThan(10).sec())
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .time(greaterThan(10).min())
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .time(greaterThan(10).hour())
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .time(greaterThan(10).day())
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},

                //большое количество каждой единицы измерения
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .time(greaterThan(100).sec())
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .time(greaterThan(100).min())
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .time(greaterThan(100).hour())
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},
                {user("2014-01-01", "2014-01-01",
                        cond("ym:s", dimension("ym:s:startURL").matchSubstring("yandex"))
                                .time(greaterThan(10000).day())
                                .cond("ym:pv", dimension("ym:pv:URL").matchSubstring("google")))},

        });
    }

    @IgnoreParameters.Tag(name = "METRIQA-3715")
    public static Collection<Object[]> ignoreParameterMaximumAllowedCond() {
        return asList(new Object[][]{
                {user("2014-01-01", "2014-01-01", user.onFilterSteps().getConditionSequence(MAXIMUM_ALLOWED_COND))}
        });
    }

    @Test
    @IgnoreParameters(reason = "DB::Exception: Maximum parse depth exceeded", tag = "METRIQA-3715")
    public void filterSyntaxUserTest() {
        user.onReportSteps().getTableReportAndExpectSuccess(
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
