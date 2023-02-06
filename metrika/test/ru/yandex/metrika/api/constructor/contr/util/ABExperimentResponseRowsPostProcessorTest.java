package ru.yandex.metrika.api.constructor.contr.util;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.api.constructor.params.ConstructorParams;
import ru.yandex.metrika.api.constructor.params.DrillDownParams;
import ru.yandex.metrika.api.constructor.response.DrillDownRow;
import ru.yandex.metrika.api.constructor.response.StaticRow;
import ru.yandex.metrika.managers.ExperimentSegment;
import ru.yandex.metrika.segments.core.dao.ApiResponse;
import ru.yandex.metrika.segments.core.meta.AttributeMeta;
import ru.yandex.metrika.segments.core.meta.MetricMeta;
import ru.yandex.metrika.segments.core.type.MetricType;
import ru.yandex.metrika.segments.site.bundles.visits.AdditionalMetricTypes;
import ru.yandex.metrika.util.client.ExperimentClient;
import ru.yandex.metrika.util.collections.F;

import static java.util.Arrays.asList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.arrayContaining;
import static org.hamcrest.Matchers.closeTo;
import static org.hamcrest.Matchers.contains;
import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.Matchers.instanceOf;
import static org.hamcrest.Matchers.nullValue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

public class ABExperimentResponseRowsPostProcessorTest {
    private ABExperimentResponseRowsPostProcessor rowsPostProcessor = new ABExperimentResponseRowsPostProcessor();
    private ExperimentClient experimentClient;
    private ApiResponse apiResponse;

    @Before
    public void before() {
        rowsPostProcessor.setSigma(1.);
        experimentClient = mock(ExperimentClient.class);
        ExperimentSegment segmentA = new ExperimentSegment();
        segmentA.setStart(0);
        segmentA.setEnd(900000);
        segmentA.setExperimentId(704);
        segmentA.setId(2523);
        ExperimentSegment segmentB = new ExperimentSegment();
        segmentB.setStart(900000);
        segmentB.setEnd(1000000);
        segmentB.setExperimentId(704);
        segmentB.setId(2524);
        when(experimentClient.getExperimentSegments(asList(2523, 2524))).thenReturn(asList(segmentA, segmentB));
        apiResponse = prepareApiResponse();
    }

    @Test
    public void testStatic() {
        List<StaticRow> staticRows = prepareValidStaticData();
        ConstructorParams params = new ConstructorParams();
        params.setReferenceRowId(asList("2524"));
        rowsPostProcessor.processStatic(staticRows, apiResponse, params);
        assertThat(staticRows, contains(hasProperty("extendedMetrics",
                arrayContaining(
                        //visits
                        allOf(hasProperty("coefToReference", closeTo(0.92540926, 0.00000001)),
                                hasProperty("value", closeTo(25191327 * (1.0 / 9.0), 0.00000001)),
                                hasProperty("error", closeTo(0.00060853, 0.00000001)
                                )),
                        //conversionRate
                        allOf(hasProperty("coefToReference", closeTo(1.6235958311, 0.00000001)),
                                hasProperty("value", closeTo(0.02633979, 0.00000001)),
                                hasProperty("error", closeTo(0.07873803, 0.00000001)
                                )))
                ),
                hasProperty("extendedMetrics", nullValue())
        ));
    }

    @Test
    public void testDrillDown() {
        List<DrillDownRow> drilldownRows = prepareValidDrillDownData();
        DrillDownParams params = new DrillDownParams();
        params.setReferenceRowId(asList("2524"));
        rowsPostProcessor.processDrilldown(drilldownRows, apiResponse, params);
        assertThat(drilldownRows, contains(hasProperty("extendedMetrics",
                arrayContaining(
                        //visits
                        allOf(hasProperty("coefToReference", closeTo(0.92540926, 0.00000001)),
                                hasProperty("value", closeTo(25191327 * (1.0 / 9.0), 0.00000001)),
                                hasProperty("error", closeTo(0.00060853, 0.00000001)
                                )),
                        //conversionRate
                        allOf(hasProperty("coefToReference", closeTo(1.6235958311, 0.00000001)),
                                hasProperty("value", closeTo(0.02633979, 0.00000001)),
                                hasProperty("error", closeTo(0.07873803, 0.00000001)
                                )))
                ),
                hasProperty("extendedMetrics", nullValue())
        ));
    }

    @Test
    public void testNoReferenceRowIdStatic() {
        List<StaticRow> staticRows = prepareValidStaticData();
        rowsPostProcessor.processStatic(staticRows, apiResponse, new ConstructorParams());
        assertThat(staticRows, everyItem(instanceOf(StaticRow.class)));
    }

    @Test
    public void testNoReferenceRowIdDrillDown() {
        List<DrillDownRow> drillDownRows = prepareValidDrillDownData();
        rowsPostProcessor.processDrilldown(drillDownRows, apiResponse, new DrillDownParams());
        assertThat(drillDownRows, everyItem(instanceOf(DrillDownRow.class)));
    }

    private List<StaticRow> prepareValidStaticData() {
        ArrayList<StaticRow> staticRows = new ArrayList<>();
        StaticRow rowA = new StaticRow();
        List<Map<String, String>> dimensionsA = new ArrayList<>();
        Map<String, String> experimentADim = new HashMap<>();
        experimentADim.put("id", "2523");
        experimentADim.put("name", "A");
        experimentADim.put("direct_id", "900000");
        Double[] metricsA = new Double[3];
        metricsA[0] = 25191327.;  //users
        metricsA[1] = 0.02633979; //conversionRate
        metricsA[2] = 540.; //visits
        rowA.setMetrics(metricsA);
        dimensionsA.add(experimentADim);
        rowA.setDimensions(dimensionsA);
        staticRows.add(rowA);
        List<Map<String, String>> dimensionsB = new ArrayList<>();
        StaticRow rowB = new StaticRow();
        Double[] metricsB = new Double[3];
        metricsB[0] = 3024647.;   //users
        metricsB[1] = 0.01622312; //conversionRate
        metricsB[2] = 230.; //visits
        Map<String, String> experimentBDim = new HashMap<>();
        experimentBDim.put("id", "2524");
        experimentBDim.put("name", "B");
        experimentBDim.put("direct_id", "100000");
        dimensionsB.add(experimentBDim);
        rowB.setMetrics(metricsB);
        rowB.setDimensions(dimensionsB);
        staticRows.add(rowB);
        return staticRows;
    }

    private List<DrillDownRow> prepareValidDrillDownData() {
        ArrayList<DrillDownRow> drillDownRows = new ArrayList<>();
        DrillDownRow rowA = new DrillDownRow();
        Double[] metricsA = new Double[3];
        metricsA[0] = 25191327.;  //users
        metricsA[1] = 0.02633979; //conversionRate
        metricsA[2] = 540.; //visits
        Map<String, String> experimentADim = new HashMap<>();
        experimentADim.put("id", "2523");
        experimentADim.put("name", "A");
        experimentADim.put("direct_id", "900000");
        rowA.setMetrics(metricsA);
        rowA.setDimension(experimentADim);
        drillDownRows.add(rowA);
        DrillDownRow rowB = new DrillDownRow();
        Double[] metricsB = new Double[3];
        metricsB[0] = 3024647.;   //users
        metricsB[1] = 0.01622312; //conversionRate
        metricsB[2] = 230.; //visits
        Map<String, String> experimentBDim = new HashMap<>();
        experimentBDim.put("id", "2524");
        experimentBDim.put("name", "B");
        experimentBDim.put("direct_id", "100000");
        rowB.setMetrics(metricsB);
        rowB.setDimension(experimentBDim);
        drillDownRows.add(rowB);
        return drillDownRows;
    }

    private ApiResponse prepareApiResponse() {
        ApiResponse apiResponse = new ApiResponse();
        MetricMeta ym_s_users = new MetricMeta();
        double GOAL_ALPHA = 1.;
        ym_s_users.setExperimentsAlpha(GOAL_ALPHA);
        ym_s_users.setMetricString("ym:s:users");
        ym_s_users.setMetricType(MetricType.INT);
//        ym_s_users.setAdditionalMetric("goal<goal_id>users");
        ym_s_users.setComparableInExperiments(true);
        MetricMeta ym_s_goal_id_conversion_rate = new MetricMeta();
        ym_s_goal_id_conversion_rate.setExperimentsAlpha(GOAL_ALPHA);
        ym_s_goal_id_conversion_rate.setMetricString("ym:s:goal<2899978>conversionRate");
        ym_s_goal_id_conversion_rate.setMetricType(MetricType.PERCENTS);
        ym_s_goal_id_conversion_rate.setAdditionalMetric(AdditionalMetricTypes.EXPERIMENT_AB, "ym:s:goal<2899978>visits");
        ym_s_goal_id_conversion_rate.setComparableInExperiments(true);
        MetricMeta ym_s_goal_id_visits = new MetricMeta();
        ym_s_goal_id_visits.setIsAdditionalMetric(true);
        ym_s_goal_id_visits.setMetricString("ym:s:goal<2899978>visits");
        ym_s_goal_id_visits.setMetricType(MetricType.INT);
        ym_s_goal_id_visits.setComparableInExperiments(true);
        ym_s_goal_id_visits.setExperimentsAlpha(GOAL_ALPHA);
        ArrayList<MetricMeta> metrics = new ArrayList<>(asList(ym_s_users, ym_s_goal_id_conversion_rate, ym_s_goal_id_visits));
        apiResponse.setMetricAttributes(metrics);
        AttributeMeta experimentDimensionMeta = new AttributeMeta();
        experimentDimensionMeta.setDim("ym:s:experimentAB704");
        experimentDimensionMeta.setDimension(true);
        experimentDimensionMeta.setAdditionalFunc(Optional.of((Function<List<Integer>, List<ExperimentSegment>>) (List<Integer> segmentIds) -> experimentClient.getExperimentSegments(segmentIds)));
        apiResponse.setDimensionAttributes(asList(experimentDimensionMeta));
        apiResponse.setNames(asList(experimentDimensionMeta.getDim()), F.map(metrics, MetricMeta::getMetricString), Collections.singletonList(metrics.get(0).getMetricString()));
        return apiResponse;
    }
}
