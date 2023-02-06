package ru.yandex.metrika.segments.core.parser;

import java.util.Optional;

import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.segments.core.parser.metric.AttributeMetricFactory;
import ru.yandex.metrika.segments.core.parser.metric.MetricFactory;
import ru.yandex.metrika.segments.core.query.metric.AggregateMetric;
import ru.yandex.metrika.segments.core.query.metric.Metric;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParamsImpl;
import ru.yandex.metrika.segments.core.query.paramertization.ParameterMap;
import ru.yandex.metrika.segments.core.query.parts.Aggregates;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 * @author jkee
 */

public class MetricParserTest {

    private QueryParserImplTest queryParserTest;
    TestAttributeBundle bundle = new TestAttributeBundle();
    private MetricParser metricParser;
    private MetricParser withParam;
    private AggregateMetric metric;

    @Before
    public void setUp() throws Exception {
        queryParserTest = new QueryParserImplTest();
        queryParserTest.setUp();
        metric = bundle.feijoaCount.getMetric(Aggregates.SUM);

        AttributeParamsImpl attributeParams = new AttributeParamsImpl();
        MetricFactory metricFactory = new AttributeMetricFactory(bundle.feijoaCount, Aggregates.SUM, Optional.empty());
        metricParser = new MetricParser("test:количествоФейхоа", attributeParams, metricFactory, null);
        MetricFactory paramMF = new AttributeMetricFactory(bundle.feijoaCount, Aggregates.SUM, Optional.empty()) {
            @Override
            public Metric build(ParameterMap parameterMap) {
                assertTrue(parameterMap.containsKey(attributeParams.getGroupParam()));
                assertEquals("day", parameterMap.get(attributeParams.getGroupParam()));
                return super.build(parameterMap);
            }
        };
        withParam = new MetricParser("test:количество<group>Фейхоа", attributeParams, paramMF, null);

    }

    @Test
    public void testParse() {
        Metric parse = metricParser.parseMetricNullable("test:количествоФейхоа");
        assertEquals(metric, parse);

        Metric param = withParam.parseMetricNullable("test:количествоdayФейхоа");
        assertEquals(metric, param);
    }
}
