package ru.yandex.autotests.metrika.appmetrica.tests.b2b;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.ArrayUtils;
import org.hamcrest.Matcher;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1SegmentTreeGETSchema;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.Tables;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.matchers.B2BMatchers;
import ru.yandex.autotests.metrika.appmetrica.matchers.ProfileB2BMatchers;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonFrontParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.addTestParameter;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnResponses;


/**
 * Проверка ручек получения деревьев сегментации
 */
@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.DIMENSIONS, Requirements.Story.METRICS
})
@Title("B2B деревьев фильтров сегментации")
@RunWith(Parameterized.class)
public class SegmentationTreeComparisonTest {

    private static final UserSteps onTesting = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps onReference = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();

    @Parameterized.Parameter
    public Application application;

    @Parameterized.Parameter(1)
    public List<String> dimensions;

    @Parameterized.Parameter(2)
    public String metric;

    @Parameterized.Parameter(3)
    public String startDate;

    @Parameterized.Parameter(4)
    public String endDate;

    @Parameterized.Parameter(5)
    public Tables table;

    private CommonFrontParameters parameters;

    @Parameterized.Parameters(name = "Application: {0}, dimensions: {1}, metric: {2}")
    public static Collection<Object[]> createParameters() {
        List<String> regionDimension = ImmutableList.of("regionCountry", "regionArea", "regionCity");
        List<String> osDimension = ImmutableList.of("operatingSystemInfo", "osMajorVersionInfo", "operatingSystemVersionInfo");
        List<String> trackerParams = ImmutableList.of("urlParamKey", "urlParamValue");
        List<String> pushCampaigns = ImmutableList.of("campaignOrGroup", "hypothesisOrTag");

        return CombinatorialBuilder.builder()
                .values(ImmutableList.of(Applications.YANDEX_REALTY))
                .values(ImmutableList.<Object[]>builder()
                        .add(params(Tables.SESSIONS, regionDimension))
                        .add(params(Tables.PROFILES, regionDimension))
                        .add(params(Tables.DEVICES, regionDimension))

                        .add(params(Tables.SESSIONS, osDimension))
                        .add(params(Tables.PROFILES, osDimension))
                        .add(params(Tables.DEVICES, osDimension))

                        .add(params(Tables.INSTALLATIONS, trackerParams))
                        .add(params(Tables.TRAFFIC_SOURCES, trackerParams))
                        .add(params(Tables.DEEPLINKS, trackerParams))

                        .add(params(Tables.PUSH_CAMPAIGNS, pushCampaigns,
                                apiProperties().getPushStartDate(), apiProperties().getPushEndDate()))

                        .build())
                .build()
                .stream()
                .map(arr -> {
                    Object applicationId = arr[0];
                    Object[] params = (Object[]) arr[1];
                    return ArrayUtils.addAll(new Object[]{applicationId}, params);
                })
                .collect(Collectors.toList());
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(application);

        // TODO MOBMET-15836
        String accuracy = table == Tables.TRAFFIC_SOURCES ? "1" : "0.5";
        parameters = new TableReportParameters()
                .withId(application)
                .withDate1(startDate)
                .withDate2(endDate)
                .withDimensions(dimensions)
                .withMetric(metric)
                // повышенный limit с малым значениям семплинга может приводить к мигающим тестам
                // при запросам по профилям из-за меняющейся сортировки
                .withAccuracy(accuracy)
                // берём лимит больше стандартных 10-ти чтобы в ответе у нас правда
                // получилось дерево с разными регионами, а не одни города подмосковья
                .withLimit(50)
                .withLang("ru")
                .withRequestDomain("ru");
    }

    @Test
    @Stories({Requirements.Story.Type.TREE})
    public void test() {
        addTestParameter("Параметры", parameters.toString());

        StatV1SegmentTreeGETSchema testingBean = onTesting.onReportSteps().getTree(parameters);
        StatV1SegmentTreeGETSchema referenceBean = onReference.onReportSteps().getTree(parameters);

        assumeOnResponses(testingBean, referenceBean);

        assertThat("ответы совпадают", testingBean, getMatcher(referenceBean));
    }

    private Matcher<StatV1SegmentTreeGETSchema> getMatcher(StatV1SegmentTreeGETSchema referenceBean) {
        if (table == Tables.DEVICES || table == Tables.PROFILES) {
            return ProfileB2BMatchers.similarProfiles(referenceBean);
        } else {
            return B2BMatchers.similarTo(referenceBean);
        }
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

    private static Object[] params(Tables table, List<String> dimensions) {
        return params(table, dimensions, apiProperties().getDefaultStartDate(), apiProperties().getDefaultEndDate());
    }

    private static Object[] params(Tables table, List<String> dimensions, String startDate, String endDate) {
        String namespace = table.getNamespace();
        List<String> dimensionsWithNs = dimensions.stream().map(d -> namespace + d).collect(Collectors.toList());
        return new Object[]{
                dimensionsWithNs,
                namespace + "users",
                startDate,
                endDate,
                table
        };
    }

}
