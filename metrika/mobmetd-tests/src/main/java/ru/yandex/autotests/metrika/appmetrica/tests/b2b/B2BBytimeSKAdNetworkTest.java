package ru.yandex.autotests.metrika.appmetrica.tests.b2b;

import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.irt.testutils.rules.parameters.IgnoreParameters;
import ru.yandex.autotests.irt.testutils.rules.parameters.IgnoreParametersList;
import ru.yandex.autotests.irt.testutils.rules.parameters.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.SkadnetworkV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.appmetrica.core.ParallelizedParameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc.B2BParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.irt.testutils.allure.AllureUtils.addTestParameter;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.data.Tables.SKADNETWORK_POSTBACKS;
import static ru.yandex.autotests.metrika.appmetrica.matchers.B2BMatchers.similarTo;
import static ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties.apiProperties;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnResponses;
import static ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc.B2BParameters.DimensionsDomain.FILTERABLE_DIMENSIONS;

@Features(Requirements.Feature.DATA)
@Stories({
        Requirements.Story.DIMENSIONS, Requirements.Story.METRICS
})
@Title("B2B SKAdNetwork bytime")
@RunWith(ParallelizedParameterized.class)
public class B2BBytimeSKAdNetworkTest {

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
        return B2BParameters.createFor(FILTERABLE_DIMENSIONS, asList(SKADNETWORK_POSTBACKS));
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
    @Stories({Requirements.Story.Type.BYTIME})
    @IgnoreParametersList({
            @IgnoreParameters(reason = "Включить после релиза", tag = "recently_changed")
    })
    public void bytimeTest() {
        addTestParameter("Параметры", parameters.toString());

        SkadnetworkV1DataBytimeGETSchema testingBean = onTesting.onReportSKAdNetworkSteps().getByTimeReport(parameters);
        SkadnetworkV1DataBytimeGETSchema referenceBean = onReference.onReportSKAdNetworkSteps().getByTimeReport(parameters);

        assumeOnResponses(testingBean, referenceBean);

        assertThat("ответы совпадают", testingBean, similarTo(referenceBean));
    }

    @After
    public void teardown() {
        resetCurrentLayer();
    }

}
