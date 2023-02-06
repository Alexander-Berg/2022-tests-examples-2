package ru.yandex.autotests.metrika.tests.b2b.webvisor;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataVisitsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2MetadataDefaultHitDimensionsGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.HitsGridParameters;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.VisitsGridParameters;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static com.google.common.collect.ImmutableList.of;
import static java.util.Collections.singletonList;
import static org.apache.commons.collections4.ListUtils.union;
import static org.hamcrest.Matchers.greaterThanOrEqualTo;
import static org.hamcrest.Matchers.iterableWithSize;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.AT_NEW_WEBVISOR;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.WEBVISOR_HITS_GRID;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 13.08.2015.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.WebVisor.HITS_GRID})
@Title("B2B - Вебвизор: таблица просмотров")
public class B2bWebVisorHitsGridTest extends BaseB2bTest {

    private static final List<Counter> COUNTERS = of(SENDFLOWERS_RU, AT_NEW_WEBVISOR);
    private static final String START_DATE = "14daysAgo";
    private static final String END_DATE = "7daysAgo";

    private static final String VISIT_ID = "ym:s:visitID";

    private static String visitId;

    @Parameter()
    public List<String> dimensions;

    @Parameter(1)
    public Counter counter;

    @Parameters(name = "Счетчик: {1}, измерения: {0}")
    public static Collection<Object[]> createParameters() {
        WebvisorV2MetadataDefaultHitDimensionsGETSchema defaults = userOnTest.onWebVisorMetadataSteps()
                .getWebVisorDefaultHitDimensions();

        List<String> availableDimensions = userOnTest.onWebVisorMetadataSteps().getWebVisorHitDimensions();

        List<List<String>> parameters = new ArrayList<>();

        for (String dimension : availableDimensions) {
            parameters.add(union(defaults.getRequired(), singletonList(dimension)));
        }

        return CombinatorialBuilder.builder()
                .values(parameters)
                .values(COUNTERS)
                .build();
    }

    @Before
    public void setup() {
        visitId = getVisitId();

        requestType = WEBVISOR_HITS_GRID;

        reportParameters = new HitsGridParameters()
                .withId(counter.get(ID))
                .withDimensions(dimensions)
                .withVisitId(visitId);
    }

    private String getVisitId() {
        VisitsGridParameters visitsGridReportParameters = new VisitsGridParameters()
                .withLimit(1)
                .withId(counter.get(ID))
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withDimensions(userOnTest.onWebVisorMetadataSteps().getWebVisorDefaultVisitDimensions().getRequired());

        WebvisorV2DataVisitsGETSchema visitsGrid =
                userOnTest.onWebVisorSteps().getVisitsGridAndExpectSuccess(visitsGridReportParameters);

        List<String> visitIds = userOnTest.onResultSteps().getDimensionValues(VISIT_ID, visitsGrid);

        assertThat("для теста доступен визит", visitIds, iterableWithSize(greaterThanOrEqualTo(1)));

        return visitIds.get(0);
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
    }

}
