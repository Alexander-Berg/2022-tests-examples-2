package ru.yandex.autotests.metrika.tests.b2b.webvisor.segmentation;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Before;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2DataVisitsGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.webvisor.v2.VisitsGridParameters;
import ru.yandex.autotests.metrika.filters.Term;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;

import static java.util.Arrays.asList;
import static java.util.function.Function.identity;
import static org.apache.commons.collections4.ListUtils.union;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.WEBVISOR_VISITS_GRID;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.matches;

/**
 * Created by sourx on 30.03.17.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.WebVisor.VISITS_GRID})
@Title("B2B - Вебвизор: сегментация таблицы визитов")
public class B2bWebVisorVisitsGridSegmentationTest extends BaseB2bTest {
    private static final Counter COUNTER = SENDFLOWERS_RU;
    private static final String START_DATE = "14daysAgo";
    private static final String END_DATE = "7daysAgo";

    private List<String> defaultDimensions;
    private List<String> dimensions;

    @Parameterized.Parameter()
    public String dimension;

    @Parameterized.Parameter(1)
    public B2bWebVisorVisitsGridSegmentationTest.Holder holder;

    static class Holder {
        private Counter counter;
        private String filter;

        public Counter getCounter() {
            return counter;
        }

        public B2bWebVisorVisitsGridSegmentationTest.Holder setCounter(Counter counter) {
            this.counter = counter;
            return this;
        }

        public String getFilter() {
            return filter;
        }

        public B2bWebVisorVisitsGridSegmentationTest.Holder setFilter(String filter) {
            this.filter = filter;
            return this;
        }
    }

    @Parameterized.Parameters(name = "Измерение: {0}")
    public static Collection<Object[]> createParameters() {
        return MultiplicationBuilder.<String, String, B2bWebVisorVisitsGridSegmentationTest.Holder>builder(
                userOnTest.onWebVisorMetadataSteps().getWebVisorVisitDimensions(),
                B2bWebVisorVisitsGridSegmentationTest.Holder::new)
                .apply(any(),
                        (d, h) -> {
                            h.setCounter(COUNTER);

                            return Stream.of(Pair.of(d, h));
                        })
                .apply(matches(equalTo("ym:s:webVisorActivity")),
                        (d, h) -> {
                            h.setFilter(dimension("ym:s:webVisorActivity").equalTo("3").build());

                            return Stream.of(Pair.of(d, h));
                        })
                .build(identity());
    }

    @Before
    public void setup() {
        defaultDimensions = userOnTest.onWebVisorMetadataSteps().getWebVisorDefaultVisitDimensions().getRequired();
        dimensions = union(defaultDimensions, asList(dimension));

        requestType = WEBVISOR_VISITS_GRID;

        reportParameters = new VisitsGridParameters()
                .withId(holder.counter)
                .withDimensions(dimensions)
                .withFilters(Optional.ofNullable(holder.getFilter()).orElse(getFilter()))
                .withDate1(START_DATE)
                .withDate2(END_DATE);
    }

    private String getFilter() {
        WebvisorV2DataVisitsGETSchema result = userOnTest.onWebVisorSteps()
                .getVisitsGridAndExpectSuccess(new VisitsGridParameters()
                        .withId(holder.getCounter())
                        .withDimensions(dimensions)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)
                );

        String dimFilter = userOnTest.onWebVisorMetadataSteps().getWebvisorDimensionSegment(dimension);

        List<String> dimensionValues = userOnTest.onResultSteps().getDimensionValues(dimension, result);
        Term term = dimension(dimFilter);
        if (dimensionValues == null) {
            term.notDefined();
        } else {
            term.equalTo(dimensionValues.get(0));
        }
        return term.build();
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
    }
}
