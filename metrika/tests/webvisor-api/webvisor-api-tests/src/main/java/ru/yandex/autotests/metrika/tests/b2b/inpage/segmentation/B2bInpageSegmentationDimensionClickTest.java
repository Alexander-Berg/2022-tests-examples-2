package ru.yandex.autotests.metrika.tests.b2b.inpage.segmentation;

import java.util.Collection;
import java.util.Optional;
import java.util.stream.Stream;

import org.apache.commons.lang3.tuple.Pair;
import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.data.parameters.inpage.v1.InpageDataParameters;
import ru.yandex.autotests.metrika.steps.metadata.MetadataSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.filters.Term.dimension;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.favoriteInpage;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.matches;

/**
 * Created by sourx on 27.10.16.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Inpage.SEGMENTATION, Requirements.Story.Inpage.CLICK})
@Title("B2b - In-page аналитика: проверка сегментации карты кликов по измерениям")
@RunWith(Parameterized.class)
public class B2bInpageSegmentationDimensionClickTest extends B2bInpageSegmentationDimensionBaseTest {
    private static final String START_DATE = "14daysAgo";
    private static final String END_DATE = "7daysAgo";

    @Parameterized.Parameters(name = "dimension: {0}")
    public static Collection createParameters() {
        return MultiplicationBuilder.<String, String, Holder>builder(
                MetadataSteps.Sets.INPAGE_FAVORITE_DIMENSIONS,
                Holder::new)
                .apply(any(),
                        (d, h) -> {
                            h.setCounter(COUNTER);
                            h.setDate1(START_DATE);
                            h.setDate2(END_DATE);
                            h.setUrl(URL);

                            return Stream.of(Pair.of(d, h));
                        })
                .apply(matches(equalTo("ym:s:startURL")),
                        (d, h) -> {
                            h.setFilter(dimension("ym:s:startURL").equalTo(URL).build());

                            return Stream.of(Pair.of(d, h));
                        })
                .apply(matches(equalTo("ym:s:paramsLevel1")),
                        (d, h) -> {
                            h.setCounter(PARAMS_LEVEL_AND_SEARCH_PHRASE_COUNTER);
                            h.setUrl(PARAMS_LEVEL_AND_SEARCH_PHRASE_URL);

                            return Stream.of(Pair.of(d, h));
                        })
                .build(identity());
    }

    @Before
    public void before() {
        requestType = RequestTypes.INPAGE_CLICK;

        reportParameters = new InpageDataParameters()
                .withAccuracy("1")
                .withFilter(Optional.ofNullable(holder.getFilter()).orElse(getFilter()))
                .withId(holder.getCounter())
                .withDate1(holder.getDate1())
                .withDate2(holder.getDate2())
                .withUrl(holder.getUrl());
    }
}
