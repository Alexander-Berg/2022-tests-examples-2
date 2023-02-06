package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.optimize;

import com.google.common.collect.ImmutableList;
import org.hamcrest.Matcher;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.core.ParallelizedParameterized;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.utils.ReportType;
import ru.yandex.autotests.metrika.appmetrica.utils.ReportTypes;
import ru.yandex.autotests.metrika.appmetrica.utils.ReportUtils;
import ru.yandex.metrika.spring.profile.ProfileData;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_METRO;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;

@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.QUERY
})
@Title("Подзапросы по девайсу должны быть внутри group by на mtmobgiga")
@RunWith(ParallelizedParameterized.class)
public class SubqueryPushDownOptimizerTest {

    private static final String GENERIC_EVENTS_SQL = "mobile.generic_events";
    private static final String PROFILES_SQL = "mobile.profiles_attributes";

    private static final UserSteps steps = UserSteps.onTesting(SUPER_LIMITED);

    @Parameterized.Parameter()
    public String title;

    @Parameterized.Parameter(1)
    public ReportType<?> reportType;

    @Parameterized.Parameter(2)
    public Matcher<Iterable<String>> matcher;

    @Parameterized.Parameter(3)
    public IFormParameters parameters;

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .addAll(createParams(
                        "Оптимизация exists в профилях для mtmobgiga",
                        ReportTypes.PROFILE_REPORT,
                        insideGroupByMatcherWithoutGlobal(GENERIC_EVENTS_SQL),
                        new TableReportParameters()
                                .withId(YANDEX_METRO)
                                .withAccuracy("0.001")
                                .withDate1("today")
                                .withDate2("today")
                                .withDimension("ym:p:regionCountry")
                                .withMetric("ym:p:users,ym:p:medianDaysSinceLastVisit,ym:p:histogramUsersBySessionsCount")
                                .withFilters("exists ym:ge:device with (eventType=='EVENT_START' and specialDefaultDate>='2020-02-28' and specialDefaultDate<='2020-02-28')")))
                .addAll(createParams(
                        "Оптимизация exists в ym:s: для mtmobgiga",
                        ReportTypes.TABLE,
                        insideGroupByMatcherWithoutGlobal(GENERIC_EVENTS_SQL),
                        new TableReportParameters()
                                .withId(YANDEX_METRO)
                                .withAccuracy("0.001")
                                .withDate1("2020-03-01")
                                .withDate2("2020-03-07")
                                .withDimension("ym:s:date")
                                .withMetric("ym:s:sessions")
                                .withFilters("not exists ym:ge:device with (eventType=='EVENT_START' and specialDefaultDate>='2020-02-27' and specialDefaultDate<='2020-02-27') and " +
                                        "exists ym:ge:device with (eventType=='EVENT_START' and specialDefaultDate>='2020-02-28' and specialDefaultDate<='2020-02-28')")
                                .withSort("-ym:s:sessions")))
                .addAll(createParams(
                        "Оптимизация для пары атрибутов",
                        ReportTypes.PROFILE_REPORT,
                        insideGroupByMatcherWithoutGlobal(PROFILES_SQL),
                        new TableReportParameters()
                                .withId(YANDEX_METRO)
                                .withAccuracy("0.001")
                                .withDate1("today")
                                .withDate2("today")
                                .withDimension("ym:p:regionCountry")
                                .withMetric("ym:p:users,ym:p:medianDaysSinceLastVisit,ym:p:histogramUsersBySessionsCount")
                                .withFilters("exists ym:p:device,ym:p:profileOrigin with (regionCountry=='225')")
                                .withSort("-ym:p:users")))
// mtmoblog больше нет
//                .addAll(createParams(
//                        "Оптимизация exists не работает на mtmoblog",
//                        ReportTypes.PROFILE_REPORT,
//                        outsideGroupByMatcher(GENERIC_EVENTS_SQL),
//                        new TableReportParameters()
//                                .withId(APPMETRICA_PROD)
//                                .withAccuracy("0.1")
//                                .withDate1("today")
//                                .withDate2("today")
//                                .withDimension("ym:p:regionCountry")
//                                .withMetric("ym:p:users,ym:p:medianDaysSinceLastVisit,ym:p:histogramUsersBySessionsCount")
//                                .withFilters("exists ym:ge:device with (eventType=='EVENT_START' and specialDefaultDate>='2020-02-28' and specialDefaultDate<='2020-02-28')")))
                .addAll(createParams(
                        "Оптимизация exists не работает, если не прописан relations",
                        ReportTypes.PROFILE_REPORT,
                        outsideGroupByMatcher(PROFILES_SQL),
                        new TableReportParameters()
                                .withId(YANDEX_METRO)
                                .withAccuracy("0.001")
                                .withDate1("today")
                                .withDate2("today")
                                .withDimension("ym:p:regionCountry")
                                .withMetric("ym:p:users,ym:p:medianDaysSinceLastVisit,ym:p:histogramUsersBySessionsCount")
                                .withFilters("exists ym:p:device,ym:p:deviceID with (regionCountry=='225')")
                                .withSort("-ym:p:users")))
                .addAll(createParams(
                        "Оптимизация exists не работает, если один из атрибутов агрегат вложенного select",
                        ReportTypes.TABLE,
                        outsideGroupByMatcher(PROFILES_SQL),
                        new TableReportParameters()
                                .withId(YANDEX_METRO)
                                .withAccuracy("0.001")
                                .withDate1("2020-03-01")
                                .withDate2("2020-03-07")
                                .withMetric("ym:s:sessions")
                                .withDimension("ym:s:date")
                                .withFilters("exists ym:p:device,ym:p:profileOrigin with (regionCountry=='225')")
                                .withSort("-ym:s:sessions")))
                .build();
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(ReportTypes.extractAppId(parameters));
    }

    @Test
    public void test() {
        Object response = reportType.getReport(steps, parameters);
        UserSteps.assumeOnResponse(response);
        //noinspection unchecked
        ProfileData profileData = ((ReportType) reportType).getProfileData(response);
        List<String> clickhouseQueryList = ReportUtils.collectCHQueries(profileData);
        assertThat(title, clickhouseQueryList, matcher);
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    private static List<Object[]> createParams(String title,
                                               ReportType<?> reportType,
                                               Matcher<Iterable<String>> matcher,
                                               TableReportParameters parameters) {
        return Collections.singletonList(toArray(title, reportType, matcher, parameters));
    }

    /**
     * Первый GROUP BY обычно относится к главному запросу, потому что в подзапросах нет GROUP BY
     * При этом GROUP BY также может быть у внешнего запроса
     */
    private static Matcher<Iterable<String>> insideGroupByMatcher(String sql) {
        return everyItem(
                allOf(
                        stringContainsInOrder(Arrays.asList(sql, "GROUP BY")),
                        not(stringContainsInOrder(Arrays.asList("GROUP BY", sql)))
                )
        );
    }

    /**
     * На mobgiga надо избегать GLOBAL-ов
     */
    private static Matcher<Iterable<String>> insideGroupByMatcherWithoutGlobal(String sql) {
        return everyItem(
                allOf(
                        stringContainsInOrder(Arrays.asList(sql, "GROUP BY")),
                        not(stringContainsInOrder(Arrays.asList("GROUP BY", sql))),
                        not(containsString("GLOBAL"))
                )
        );
    }

    private static Matcher<Iterable<String>> outsideGroupByMatcher(String sql) {
        return everyItem(stringContainsInOrder(Arrays.asList("GROUP BY", sql)));
    }
}
