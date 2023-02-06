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

import java.util.Collection;
import java.util.Collections;
import java.util.List;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.SEARCH_PLUGIN;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_DISK_BETA;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;

@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.QUERY
})
@Title("Запросы с группировкой по EventID должны выполняться оптимально")
@RunWith(ParallelizedParameterized.class)
public class CrashesOptimizerTest {

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
                        "Оптимизация при группировке по errorEventObjExt для mtmobgiga",
                        ReportTypes.TABLE,
                        optimized(),
                        new TableReportParameters()
                                .withId(SEARCH_PLUGIN)
                                .withAccuracy("1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-07")
                                .withDimension("ym:er2:dateTime,ym:er2:errorEventObjExt,ym:er2:appVersionBuildNumberOrderValue")
                                .withMetric("ym:er2:errors")
                                .withFilters("ym:er2:errorGroup==12865510783704500402 AND ym:er2:operatingSystemInfo=='android'")))
                .addAll(createParams(
                        "Оптимизация при группировке по errorEventObj для mtmobgiga",
                        ReportTypes.TABLE,
                        optimized(),
                        new TableReportParameters()
                                .withId(SEARCH_PLUGIN)
                                .withAccuracy("1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-07")
                                .withDimension("ym:er2:dateTime,ym:er2:errorEventObj,ym:er2:appVersionBuildNumberOrderValue")
                                .withMetric("ym:er2:errors")
                                .withFilters("ym:er2:errorGroup==12865510783704500402 AND ym:er2:operatingSystemInfo=='android'")))
                .addAll(createParams(
                        "Оптимизация не работает при произвольной группировке",
                        ReportTypes.TABLE,
                        notOptimized(),
                        new TableReportParameters()
                                .withId(SEARCH_PLUGIN)
                                .withAccuracy("0.1")
                                .withDate1("today")
                                .withDate2("today")
                                .withDimension("ym:er2:errorGroupObj")
                                .withMetric("ym:er2:errors,norm(ym:er2:errors),ym:er2:errorDevices,norm(ym:er2:errorDevices),ym:er2:errorsDevicesPercentage,ym:er2:errorsUndecoded")
                                .withFilters("ym:er2:operatingSystemInfo=='android'")))
                .addAll(createParams(
                        "Оптимизация не работает без вложенного запроса",
                        ReportTypes.TABLE,
                        notOptimized(),
                        new TableReportParameters()
                                .withId(YANDEX_DISK_BETA)
                                .withAccuracy("0.1")
                                .withDate1("2020-05-01")
                                .withDate2("2020-05-08")
                                .withDimension("ym:er:dateTime,ym:er:errorEventObjExt")
                                .withMetric("ym:er:errors")
                                .withFilters("ym:er:operatingSystemInfo=='android'")
                                .withIncludeUndefined(true)))
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
        //noinspection unchecked,rawtypes
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

    private static Matcher<Iterable<String>> optimized() {
        return everyItem(containsString("distributed_group_by_no_merge"));
    }

    private static Matcher<Iterable<String>> notOptimized() {
        return everyItem(not(containsString("distributed_group_by_no_merge")));
    }
}
