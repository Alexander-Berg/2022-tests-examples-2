package ru.yandex.metrika.segments.core.parser;

import java.util.Optional;

import org.junit.Assert;
import org.junit.Test;

import ru.yandex.metrika.segments.apps.bundles.AppAttributeParams;
import ru.yandex.metrika.segments.apps.bundles.funnels.param.FunnelPatternParamMetaFactory;
import ru.yandex.metrika.segments.apps.bundles.funnels.param.FunnelRestrictionParamMetaFactory;
import ru.yandex.metrika.segments.core.query.paramertization.ParameterMap;

public class IdParserNegativeTest {

    private final AppAttributeParams param = new AppAttributeParams(
            new FunnelPatternParamMetaFactory(null), new FunnelRestrictionParamMetaFactory(null));

    @Test
    public void testUrlParametersNegative() {
        IdParser parser = new IdParser("urlParameter<url_parameter_key>", param);
        Optional<ParameterMap> result = parser.parse("urlParameterutm source");
        Assert.assertTrue(result.isEmpty());
    }

    @Test
    public void testUrlParametersNegative2() {
        IdParser parser = new IdParser("urlParameter<url_parameter_key>", param);
        Optional<ParameterMap> result = parser.parse("urlParameterSELECT`secret`");
        Assert.assertTrue(result.isEmpty());
    }

    @Test
    public void testUrlParametersNegative3() {
        IdParser parser = new IdParser("urlParameter<url_parameter_key>", param);
        Optional<ParameterMap> result = parser.parse("urlParameterSELECT'secret'");
        Assert.assertTrue(result.isEmpty());
    }
}
