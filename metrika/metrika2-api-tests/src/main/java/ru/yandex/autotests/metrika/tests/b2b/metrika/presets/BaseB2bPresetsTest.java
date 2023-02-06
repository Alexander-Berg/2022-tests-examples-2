package ru.yandex.autotests.metrika.tests.b2b.metrika.presets;

import java.util.Collection;
import java.util.Map;

import com.google.common.collect.ImmutableMap;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.PresetWrapper;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bTest;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.ECOMMERCE_TEST;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.KVAZI_KAZINO;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_CDP;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_EATS_ON_MAPS;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_WEATHER;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.ecommerce;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.table;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.yan;

/**
 * Created by omaz on 05.12.2014.
 */
public abstract class BaseB2bPresetsTest extends BaseB2bTest {

    protected static final Counter COUNTER = SENDFLOWERS_RU;
    protected static Map<String, Counter> PRESET_TO_COUNTER = ImmutableMap.<String, Counter>builder()
            .put("offline_visits_pvl", ECOMMERCE_TEST)
            .put("offline_calls_quality", ECOMMERCE_TEST)
            .put("offline_calls_sources", ECOMMERCE_TEST)
            .put("adfox_defaults", ECOMMERCE_TEST)
            .put("adfox_geo", ECOMMERCE_TEST)
            .put("adfox_urls", ECOMMERCE_TEST)
            .put("adfox_invent", ECOMMERCE_TEST)
            .put("adfox_shows", ECOMMERCE_TEST)
            .put("adfox_puids", ECOMMERCE_TEST)
            .put("adfox_sources", ECOMMERCE_TEST)
            .put("adfox_header_bidding", ECOMMERCE_TEST)
            .put("publishers_materials", ECOMMERCE_TEST)
            .put("publishers_sources", ECOMMERCE_TEST)
            .put("publishers_rubrics", ECOMMERCE_TEST)
            .put("publishers_authors", ECOMMERCE_TEST)
            .put("publishers_thematics", ECOMMERCE_TEST)
            .put("recommendation_widget_articles", YANDEX_WEATHER)
            .put("recommendation_widget_page", YANDEX_WEATHER)
            .put("recommendation_widget_conversion", YANDEX_WEATHER)
            .put("experiment_ab", KVAZI_KAZINO)
            .put("vacuum", YANDEX_EATS_ON_MAPS)
            .put("cdp_orders", TEST_CDP)
            .put("orders_sources", TEST_CDP)
            .put("sources_expenses_and_roi", TEST_CDP)
            .build();

    @Parameterized.Parameter()
    public PresetWrapper preset;

    @Parameterized.Parameters(name = "{0}")
    public static Collection createParameters() {
        return userOnTest.onMetadataSteps().getPresetsMeta(
                table(TableEnum.VISITS).or(table(TableEnum.HITS)).and(ecommerce().negate()).and(yan().negate())).stream()
                .map(p -> toArray(new PresetWrapper(p)))
                .collect(toList());
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
    }

    protected long getCounterId() {
        return PRESET_TO_COUNTER.getOrDefault(preset.getPreset().getName(), COUNTER).get(Counter.ID);
    }
}
