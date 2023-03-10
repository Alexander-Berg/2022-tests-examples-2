package ru.yandex.autotests.metrika.appmetrica.tests.b2b;

import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataDrilldownGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.appmetrica.core.ParallelizedParameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc.B2BParameters;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParametersList;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.addTestParameter;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.data.Tables.DEVICES;
import static ru.yandex.autotests.metrika.appmetrica.data.Tables.PROFILES;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ProfileB2BMatchers.similarProfiles;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnResponses;
import static ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc.B2BParameters.DimensionsDomain.ALL_DIMENSIONS;

/**
 * Created by konkov on 04.05.2016.
 */
@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.DIMENSIONS, Requirements.Story.METRICS
})
@Title("Profile B2B")
@RunWith(ParallelizedParameterized.class)
public class B2BProfilesTest {

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

    @Parameterized.Parameters(name = "{0},{1}")
    public static Collection<Object[]> createParameters() {
        return B2BParameters.createFor(ALL_DIMENSIONS, asList(PROFILES, DEVICES));
    }

    @IgnoreParameters.Tag(name = "recently_changed")
    public static Collection<Object[]> ignoredParamsAsRecentlyChanged() {
        return B2BParameters.ignoredParamsAsRecentlyChanged();
    }

    @Before
    public void setup() {
        setCurrentLayerByApp(Long.parseLong(parameters.get("id")));
    }

    @Test
    @Stories({Requirements.Story.Type.TABLE})
    @IgnoreParametersList({
            @IgnoreParameters(reason = "???????????????? ?????????? ????????????", tag = "recently_changed")
    })
    public void tableTest() {
        addTestParameter("??????????????????", parameters.toString());

        StatV1DataGETSchema testingBean = onTesting.onReportSteps().getTableReport(parameters);
        StatV1DataGETSchema referenceBean = onReference.onReportSteps().getTableReport(parameters);

        assumeOnResponses(testingBean, referenceBean);

        assertThat("???????????? ??????????????????", testingBean, similarProfiles(referenceBean));
    }

    @Test
    @Stories({Requirements.Story.Type.DRILLDOWN})
    @IgnoreParametersList({
            @IgnoreParameters(reason = "???????????????? ?????????? ????????????", tag = "recently_changed")
    })
    public void drilldownTest() {
        addTestParameter("??????????????????", parameters.toString());

        StatV1DataDrilldownGETSchema testingBean = onTesting.onReportSteps().getDrillDownReport(parameters);
        StatV1DataDrilldownGETSchema referenceBean = onReference.onReportSteps().getDrillDownReport(parameters);

        assumeOnResponses(testingBean, referenceBean);

        assertThat("???????????? ??????????????????", testingBean, similarProfiles(referenceBean));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

}
