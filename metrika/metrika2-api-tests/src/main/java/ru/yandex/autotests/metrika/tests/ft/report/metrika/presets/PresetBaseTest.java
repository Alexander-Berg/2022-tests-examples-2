package ru.yandex.autotests.metrika.tests.ft.report.metrika.presets;

import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableMap;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;

import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.metadata.v1.ParameterValues;
import ru.yandex.autotests.metrika.data.metadata.v1.PresetWrapper;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.Feature;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;
import ru.yandex.metrika.api.constructor.response.QueryExternal;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static org.apache.commons.lang3.StringUtils.isNotEmpty;
import static org.hamcrest.Matchers.equalTo;
import static org.junit.runners.Parameterized.Parameter;
import static ru.yandex.autotests.irt.testutils.matchers.CompositeMatcher.matchEvery;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.DRESSTOP;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.ECOMMERCE_TEST;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.KVAZI_KAZINO;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.SENDFLOWERS_RU;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_CDP;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_EATS_ON_MAPS;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_WEATHER;
import static ru.yandex.autotests.metrika.data.metadata.v1.ParameterValues.getDefaults;
import static ru.yandex.autotests.metrika.matchers.SortMatcher.isSortEqualTo;
import static ru.yandex.autotests.metrika.sort.SortBuilder.sort;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.metric;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.AllureUtils.attachPreset;

/**
 * Created by konkov on 03.09.2014.
 */
public abstract class PresetBaseTest {

    @Rule
    public ParametersIgnoreRule parametersIgnoreRule = new ParametersIgnoreRule();

    /**
     * user инициализируется статически, т.к. он используется на этапе
     * формирования перечня параметров теста
     */
    protected static final UserSteps user = new UserSteps().withDefaultAccuracy();

    protected static final Counter COUNTER = SENDFLOWERS_RU;
    protected static final Counter COUNTER_ADVERTISING = DRESSTOP;
    protected static final Counter USER_PARAM_COUNTER = Counters.YANDEX_METRIKA_2_0;
    protected static final String START_DATE = "2015-06-20";
    protected static final String END_DATE = "2015-06-20";

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
            .put("basket", ECOMMERCE_TEST)
            .put("basket_products", ECOMMERCE_TEST)
            .put("coupon", ECOMMERCE_TEST)
            .put("purchase", ECOMMERCE_TEST)
            .put("top_brands", ECOMMERCE_TEST)
            .put("top_products", ECOMMERCE_TEST)
            .put("recommendation_widget_articles", YANDEX_WEATHER)
            .put("recommendation_widget_page", YANDEX_WEATHER)
            .put("recommendation_widget_conversion", YANDEX_WEATHER)
            .put("experiment_ab", KVAZI_KAZINO)
            .put("vacuum", YANDEX_EATS_ON_MAPS)
            .put("cdp_orders", TEST_CDP)
            .put("orders_sources", TEST_CDP)
            .put("sources_expenses_and_roi", TEST_CDP)
            .put("content_user_params", USER_PARAM_COUNTER)
            .put("sources_direct_clicks", COUNTER_ADVERTISING)
            .build();

    @Parameter()
    public PresetWrapper parameter;

    protected TableReportParameters reportParameters;
    protected StatV1DataGETSchema result;

    protected List<String> expectedDimensions;
    protected List<String> expectedMetrics;
    protected String expectedSort;

    protected ParameterValues getDefaultParameters() {
        return getDefaults(PRESET_TO_COUNTER.getOrDefault(parameter.getPreset().getName(), COUNTER));
    }

    protected TableReportParameters getReportParameters() {
        return new TableReportParameters()
                .withId(PRESET_TO_COUNTER.getOrDefault(parameter.getPreset().getName(), COUNTER).get(Counter.ID))
                .withPreset(parameter.getPreset().getName())
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withAccuracy("low");
    }

    @Before
    public void setup() {
        reportParameters = getReportParameters();

        attachPreset(parameter);

        expectedDimensions = with(parameter.getPreset().getDimensions()).convert(getDefaultParameters().getSubstitute());

        List<String> presetMetrics = parameter.getPreset().getMetrics();
        Map<String, MetricMetaExternal> metricMetas = user.onMetadataSteps().getMetricsMeta(metric(presetMetrics::contains))
                .stream().collect(Collectors.toMap(MetricMetaExternal::getDim, Function.identity()));
        Set<Feature> counterFeatures = new HashSet<>(user.onManagementSteps().onCountersSteps()
                .getCounterInfo(PRESET_TO_COUNTER.getOrDefault(parameter.getPreset().getName(), COUNTER).get(Counter.ID))
                .getFeatures());
        expectedMetrics = with(
                presetMetrics.stream()
                        .filter(
                                metricName -> {
                                    if (metricMetas.get(metricName).getFeatures() == null) {
                                        return true;
                                    }
                                    return counterFeatures.containsAll(metricMetas.get(metricName).getFeatures());
                                }
                        ).collect(Collectors.toList())
        ).convert(getDefaultParameters().getSubstitute());

        expectedSort = isNotEmpty(parameter.getPreset().getSort()) ?
                getDefaultParameters().substitute(parameter.getPreset().getSort()) :
                getDefaultParameters().substitute(sort().by(expectedMetrics.get(0)).descending().build());

        result = user.onReportSteps().getTableReportAndExpectSuccess(reportParameters,
                getDefaultParameters().toFormParameters());
    }

    @Test
    public void checkQuery() {
        assertThat("результат содержит измерения, метрики и сортировку из шаблона",
                result.getQuery(), matchEvery(
                        having(on(QueryExternal.class).getDimensions(), equalTo(expectedDimensions)),
                        having(on(QueryExternal.class).getMetrics(), equalTo(expectedMetrics)),
                        having(on(QueryExternal.class).getSort(), isSortEqualTo(expectedSort))));
    }
}
