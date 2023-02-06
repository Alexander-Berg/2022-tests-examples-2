package ru.yandex.autotests.metrika.tests.b2b.webvisor;

import org.junit.Before;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2MetadataDefaultVisitDimensionsGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
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
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.AT_NEW_WEBVISOR;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.WEBVISOR_VISITS_GRID;

/**
 * Created by konkov on 13.08.2015.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.WebVisor.VISITS_GRID})
@Title("B2B - Вебвизор: таблица визитов")
public class B2bWebVisorVisitsGridTest extends BaseB2bTest {

    private static final List<Counter> COUNTERS = of(SENDFLOWERS_RU, AT_NEW_WEBVISOR);
    private static final String START_DATE = "14daysAgo";
    private static final String END_DATE = "7daysAgo";

    @Parameter()
    public List<String> dimensions;

    @Parameter(1)
    public Counter counter;

    @Parameters(name = "Счетчик: {1}, измерения: {0}")
    public static Collection<Object[]> createParameters() {
        WebvisorV2MetadataDefaultVisitDimensionsGETSchema defaults = userOnTest.onWebVisorMetadataSteps()
                .getWebVisorDefaultVisitDimensions();

        List<String> availableDimensions = userOnTest.onWebVisorMetadataSteps().getWebVisorVisitDimensions();

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
        requestType = WEBVISOR_VISITS_GRID;

        reportParameters = new VisitsGridParameters()
                .withId(counter.get(ID))
                .withDimensions(dimensions)
                .withDate1(START_DATE)
                .withDate2(END_DATE);
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
    }
}
