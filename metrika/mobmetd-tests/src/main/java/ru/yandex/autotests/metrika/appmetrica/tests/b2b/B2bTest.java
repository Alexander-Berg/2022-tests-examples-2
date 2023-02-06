package ru.yandex.autotests.metrika.appmetrica.tests.b2b;

import com.google.common.collect.ImmutableSet;
import org.apache.commons.lang3.ArrayUtils;
import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.irt.testutils.beandiffer2.beanfield.BeanFieldPath;
import ru.yandex.autotests.irt.testutils.rules.parameters.IgnoreParameters;
import ru.yandex.autotests.irt.testutils.rules.parameters.IgnoreParametersList;
import ru.yandex.autotests.irt.testutils.rules.parameters.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.appmetrica.core.ParallelizedParameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc.B2BParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.Set;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.addTestParameter;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.data.Tables.*;
import static ru.yandex.autotests.metrika.appmetrica.matchers.B2BMatchers.similarTo;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnResponses;
import static ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc.B2BParameters.DimensionsDomain.ALL_DIMENSIONS;

@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.DIMENSIONS, Requirements.Story.METRICS
})
@Title("B2B")
@RunWith(ParallelizedParameterized.class)
public class B2bTest {

    @Rule
    public ParametersIgnoreRule ignoreRule = new ParametersIgnoreRule();

    private static final UserSteps onTesting = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiTesting())
            .withUser(Users.SUPER_LIMITED)
            .build();

    private static final UserSteps onReference = UserSteps.builder()
            .withBaseUrl(apiProperties().getApiReference())
            .withUser(Users.SUPER_LIMITED)
            .build();

    @Parameterized.Parameter()
    public String dimension;

    @Parameterized.Parameter(1)
    public String metric;

    @Parameterized.Parameter(2)
    public FreeFormParameters parameters;

    @Parameterized.Parameter(3)
    public String appId;

    private BeanFieldPath[] ignoredFields;


    @Parameterized.Parameters(name = "{0},{1},{3}")
    public static Collection<Object[]> createParameters() {
        // профили "ym:d:" тестируются отдельно в B2BProfilesTest, потому что:
        //  1. для них нет строится отчёт byTime (на самом деле строится)
        //  2. для них берётся интервал по текущий момент, поэтому постоянно далетают новые данные, в том числе между
        // запросами к тестингу и к проду, поэтому значения метрик необходимо сравнивать с погрешностью
        //
        // skadnetwork "ym:sk:" тестируются отдельно, в B2BSKAdNetworkTest, потому что для них сейчас используется отдельная ручка,
        // в которой выполняется мэппинг app_id в apple_app_id
        return B2BParameters.createWithout(ALL_DIMENSIONS, asList(PROFILES, DEVICES, SKADNETWORK_POSTBACKS));
    }

    @IgnoreParameters.Tag(name = "recently_changed")
    public static Collection<Object[]> ignoredParamsAsRecentlyChanged() {
        return B2BParameters.ignoredParamsAsRecentlyChanged();
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(Long.parseLong(parameters.get("id")));

        // ничего лучше не получилось: https://st.yandex-team.ru/MOBMET-14919
        final Set<String> dimensionsWithBrokenTotals =
                ImmutableSet.of("ym:er2:errorEventObj", "ym:er2:errorEventObjExt",
                        "ym:anr2:anrEventObj", "ym:anr2:anrEventObjExt",
                        "ym:cr2:crashEventObj", "ym:cr2:crashEventObjExt");
        if (dimensionsWithBrokenTotals.contains(dimension)) {
            ignoredFields = ArrayUtils.addAll(
                    AppMetricaApiProperties.apiProperties().getB2bIgnoredFields(),
                    BeanFieldPath.newPath("totals/0".split("/")));
        } else {
            ignoredFields = AppMetricaApiProperties.apiProperties().getB2bIgnoredFields();
        }
    }

    @Test
    @Stories({Requirements.Story.Type.TABLE})
    @IgnoreParametersList({
            @IgnoreParameters(reason = "Включить после релиза", tag = "recently_changed")
    })
    public void tableTest() {
        addTestParameter("Параметры", parameters.toString());

        StatV1DataGETSchema testingBean = onTesting.onReportSteps().getTableReport(parameters);
        StatV1DataGETSchema referenceBean = onReference.onReportSteps().getTableReport(parameters);

        assumeOnResponses(testingBean, referenceBean);

        assertThat("ответы совпадают", testingBean, similarTo(referenceBean, new BeanFieldPath[]{}, ignoredFields));
    }

    @Test
    @Stories({Requirements.Story.Type.DRILLDOWN})
    @IgnoreParametersList({
            @IgnoreParameters(reason = "Включить после релиза", tag = "recently_changed")
    })
    public void drilldownTest() {
        addTestParameter("Параметры", parameters.toString());

        StatV1DataDrilldownGETSchema testingBean = onTesting.onReportSteps().getDrillDownReport(parameters);
        StatV1DataDrilldownGETSchema referenceBean = onReference.onReportSteps().getDrillDownReport(parameters);

        assumeOnResponses(testingBean, referenceBean);

        assertThat("ответы совпадают", testingBean, similarTo(referenceBean, new BeanFieldPath[]{}, ignoredFields));
    }


    @After
    public void teardown() {
        resetCurrentLayer();
    }

}
