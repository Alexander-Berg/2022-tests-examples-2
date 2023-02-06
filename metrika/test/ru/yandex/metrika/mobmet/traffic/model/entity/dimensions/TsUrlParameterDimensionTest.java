package ru.yandex.metrika.mobmet.traffic.model.entity.dimensions;

import java.util.Collections;
import java.util.Map;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;

import ru.yandex.metrika.mobmet.misc.UrlParamNames;
import ru.yandex.metrika.mobmet.traffic.misc.TsUrlParamResolver;
import ru.yandex.metrika.mobmet.traffic.model.entity.metrics.TsUnfoldMetric;
import ru.yandex.metrika.spring.TranslationHelper;

import static org.mockito.Mockito.mock;
import static ru.yandex.metrika.mobmet.traffic.model.entity.dimensions.TsUrlParameterDimension.tryParse;
import static ru.yandex.metrika.mobmet.traffic.model.entity.dimensions.TsUrlParameterDimension.tryParseUnfoldMetric;

public class TsUrlParameterDimensionTest {

    private TsUrlParamResolver resolver;

    @Before
    public void setup() {
        TranslationHelper translationHelper = mock(TranslationHelper.class);
        UrlParamNames names = new UrlParamNames(translationHelper);
        resolver = new TsUrlParamResolver(names);
    }

    @Test
    public void testDimParse() {
        var actual = tryParse("urlParameterurm_source", resolver, Collections.emptyMap());
        Assert.assertTrue(actual.isPresent());
        TsUrlParameterDimension dim = (TsUrlParameterDimension) actual.get();
        Assert.assertEquals("urm_source", dim.getUrlKey());
    }

    @Test
    public void testDimParse2() {
        var actual = tryParse("urlParameter<url_parameter_key_1>", resolver, Map.of("url_parameter_key_1", "urm-source"));
        Assert.assertTrue(actual.isPresent());
        TsUrlParameterDimension dim = (TsUrlParameterDimension) actual.get();
        Assert.assertEquals("urm-source", dim.getUrlKey());
    }

    @Test
    public void testDimParseBadName() {
        var actual = tryParse("urlurm source", resolver, Collections.emptyMap());
        Assert.assertTrue(actual.isEmpty());
    }

    @Test
    public void testDimParseBadName2() {
        var actual = tryParse("url<url_parameter_key>", resolver, Map.of("url_parameter_key", "urm source"));
        Assert.assertTrue(actual.isEmpty());
    }

    @Test
    public void testDimParseBadParam() {
        var actual = tryParse("urlParameterurm source", resolver, Collections.emptyMap());
        Assert.assertTrue(actual.isEmpty());
    }

    @Test
    public void testDimParseBadParam2() {
        var actual = tryParse("urlParameter<url_parameter_key_1", resolver, Map.of("url_parameter_key_1", "urm source"));
        Assert.assertTrue(actual.isEmpty());
    }

    @Test
    public void testDimMissingParam() {
        var actual = tryParse("urlParameter<url_parameter_key_1>", resolver, Collections.emptyMap());
        Assert.assertTrue(actual.isEmpty());
    }

    @Test
    public void testMetricParse() {
        var actual = tryParseUnfoldMetric("hasUrlParameterurm_source", resolver, Collections.emptyMap());
        Assert.assertTrue(actual.isPresent());
        TsUnfoldMetric metric = (TsUnfoldMetric) actual.get();
        TsUrlParameterDimension dim = (TsUrlParameterDimension) metric.getEntity();
        Assert.assertEquals("urm_source", dim.getUrlKey());
    }

    @Test
    public void testMetricParse2() {
        var actual = tryParseUnfoldMetric(
                "hasUrlParameter<url_parameter_key>", resolver, Map.of("url_parameter_key", "urm_source"));
        Assert.assertTrue(actual.isPresent());
        TsUnfoldMetric metric = (TsUnfoldMetric) actual.get();
        TsUrlParameterDimension dim = (TsUrlParameterDimension) metric.getEntity();
        Assert.assertEquals("urm_source", dim.getUrlKey());
    }

    @Test
    public void testMetricParseBadParam() {
        var actual = tryParseUnfoldMetric("hasUrlParameterurm source", resolver, Collections.emptyMap());
        Assert.assertTrue(actual.isEmpty());
    }

    @Test
    public void testMetricParseBadParam2() {
        var actual = tryParseUnfoldMetric("has<url_parameter_key>", resolver,
                Map.of("<url_parameter_key>", "UrlParameterurm source"));
        Assert.assertTrue(actual.isEmpty());
    }

    @Test
    public void testMetricParseBadName() {
        var actual = tryParseUnfoldMetric("urlurm source", resolver, Collections.emptyMap());
        Assert.assertTrue(actual.isEmpty());
    }

    @Test
    public void testMetricParseBadName2() {
        var actual = tryParseUnfoldMetric("url<url_parameter_key>", resolver, Map.of("<url_parameter_key>", "a"));
        Assert.assertTrue(actual.isEmpty());
    }
}
