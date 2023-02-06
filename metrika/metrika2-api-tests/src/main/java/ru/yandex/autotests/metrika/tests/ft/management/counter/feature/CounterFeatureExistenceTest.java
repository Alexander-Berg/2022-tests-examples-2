package ru.yandex.autotests.metrika.tests.ft.management.counter.feature;

import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;
import java.util.function.Function;

import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.*;
import static ru.yandex.autotests.metrika.tests.ft.management.counter.feature.CounterFeatureExistenceTest.FeatureMatcherFactory.DOESNTHAVE;
import static ru.yandex.autotests.metrika.tests.ft.management.counter.feature.CounterFeatureExistenceTest.FeatureMatcherFactory.HAS;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.COUNTERS)
@Title("Счетчик: проверка фич")
@RunWith(Parameterized.class)
public class CounterFeatureExistenceTest {


    @Parameterized.Parameter
    public Counter counter;

    @Parameterized.Parameter(1)
    public FeatureMatcherFactory matcherFactory;

    @Parameterized.Parameter(2)
    public Feature feature;

    @Parameterized.Parameters(name = "Счетчик: {0}, ожидание: {1} фичу {2} ")
    public static Collection<Object[]> createParameters() {
        return Arrays.asList(new Object[][]{
                {SENDFLOWERS_RU, HAS, Feature.DIRECT},
                {TEST_COUNTER, DOESNTHAVE, Feature.DIRECT},
                {RECOMMENDATION_AUTO, HAS, Feature.RECOMMENDATIONS},
                {TEST_COUNTER, DOESNTHAVE, Feature.RECOMMENDATIONS},
                {GENVIC_RU, HAS, Feature.TARGET_CALLS},
                {TEST_COUNTER, DOESNTHAVE, Feature.TARGET_CALLS},
                {FORBES, HAS, Feature.TURBO_PAGE},
                {TEST_COUNTER, DOESNTHAVE, Feature.TURBO_PAGE},
                {AT_NEW_WEBVISOR, HAS, Feature.WEBVISOR_2},
                {TEST_COUNTER, DOESNTHAVE, Feature.WEBVISOR_2},
                {YANDEX_NEWS, HAS, Feature.PARTNER},
                {TEST_COUNTER, DOESNTHAVE, Feature.PARTNER},
                {EUROPA_PLUS, HAS, Feature.PUBLISHERS},
                {TEST_COUNTER, DOESNTHAVE, Feature.PUBLISHERS}
        });
    }

    private UserSteps user = new UserSteps();

    @Test
    public void check() {
        CounterFull counterFull = user.onManagementSteps().onCountersSteps().getCounterInfo(counter.get(ID));

        assertThat(String.format("наличие фичи %s соответствует ожиданию", feature.toString()), counterFull.getFeatures(), matcherFactory.forFeature(feature));
    }

    enum FeatureMatcherFactory {
        HAS(Matchers::hasItem, "имеет"),
        DOESNTHAVE(f -> not(hasItem(f)), "не имеет");

        private final Function<Feature, Matcher> featuresMatcherFactory;
        private final String text;

        FeatureMatcherFactory(Function<Feature, Matcher> featuresMatcherFactory, String text) {
            this.featuresMatcherFactory = featuresMatcherFactory;
            this.text = text;
        }

        Matcher forFeature(Feature feature) {
            return featuresMatcherFactory.apply(feature);
        }

        public String toString() {
            return text;
        }
    }
}
