package ru.yandex.metrika.segments.core.parser;

import java.util.Collection;
import java.util.Map;
import java.util.Optional;

import com.google.common.collect.ImmutableList;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.segments.apps.bundles.AppAttributeParams;
import ru.yandex.metrika.segments.apps.bundles.funnels.param.FunnelPatternParamMetaFactory;
import ru.yandex.metrika.segments.apps.bundles.funnels.param.FunnelRestrictionParamMetaFactory;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParamMeta;
import ru.yandex.metrika.segments.core.query.paramertization.ParameterMap;

import static ru.yandex.metrika.segments.apps.bundles.AppAttributeParams.eventName;
import static ru.yandex.metrika.segments.apps.bundles.AppAttributeParams.eventParamPath;


@RunWith(Parameterized.class)
public class IdParserTest {

    private final AppAttributeParams param = new AppAttributeParams(
            new FunnelPatternParamMetaFactory(null), new FunnelRestrictionParamMetaFactory(null));

    @Parameterized.Parameter
    public String attributeTemplate;

    @Parameterized.Parameter(1)
    public String apiName;

    @Parameterized.Parameter(2)
    public Map<AttributeParamMeta, String> expectedParams;

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> initParams() {
        return ImmutableList.<Object[]>builder()
                .add(params(
                        "urlParameter<url_parameter_key>",
                        "urlParameterutm_source",
                        Map.of(AppAttributeParams.urlParamKeyMeta, "utm_source")))
                .add(params(
                        "paramValue<param_value_path>",
                        "paramValue{'SELECT\\'secret\\''}",
                        Map.of(eventParamPath, "SELECT'secret'")))
                .add(params(
                        "paramValue<param_value_path>",
                        "paramValue{'}'}",
                        Map.of(eventParamPath, "}")))
                .add(params(
                        "paramValue<param_value_path>",
                        "paramValue{'SELECT\nsecret'}",
                        Map.of(eventParamPath, "SELECT\nsecret")))
                .add(params(
                        "paramValue<param_value_path>Suffix",
                        "paramValue{'}Suffix'}Suffix",
                        Map.of(eventParamPath, "}Suffix")))
                .add(params(
                        "paramValue<param_value_path>Suffix",
                        "paramValue{'\\'}Suffix'}Suffix",
                        Map.of(eventParamPath, "'}Suffix")))
                .add(params(
                        "paramValue<event_name>Some<param_value_path>Again",
                        "paramValue<event_name>Some<param_value_path>Again",
                        Map.of(eventName, "<event_name>", eventParamPath, "<param_value_path>")))
                .add(params(
                        "paramValue<event_name>Some<param_value_path>Again",
                        "paramValue{'myEvent'}Some<param_value_path>Again",
                        Map.of(eventName, "myEvent", eventParamPath, "<param_value_path>")))
                .add(params(
                        "paramValue<event_name>Some<param_value_path>Again",
                        "paramValuemyEventSome<param_value_path>Again",
                        Map.of(eventName, "myEvent", eventParamPath, "<param_value_path>")))
                .add(params(
                        "paramValue<event_name>Some<param_value_path>Again",
                        "paramValue{'myEvent\\'}'}Some{'}\n\n'}Again",
                        Map.of(eventName, "myEvent'}", eventParamPath, "}\n\n")))
                .build();
    }

    @Test
    public void test() {
        IdParser parser = new IdParser(attributeTemplate, param);
        Optional<ParameterMap> result = parser.parse(apiName);
        Assert.assertTrue("Params exists", result.isPresent());
        Assert.assertEquals("Params matched", expectedParams, result.get().getValues());
    }

    private static Object[] params(Object... params) {
        return params;
    }
}
