package ru.yandex.metrika.segments.core.parser;

import java.util.Collections;
import java.util.Set;

import com.google.common.collect.Sets;
import gnu.trove.set.hash.TIntHashSet;
import org.junit.Ignore;

import ru.yandex.metrika.segments.clickhouse.ClickHouse;
import ru.yandex.metrika.segments.core.query.QueryContext;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParamMeta;
import ru.yandex.metrika.segments.core.query.paramertization.AttributeParamsImpl;
import ru.yandex.metrika.segments.core.query.paramertization.ParamValidator;
import ru.yandex.metrika.segments.core.query.paramertization.Qvalue;
import ru.yandex.metrika.segments.site.parametrization.Attribution;

/**
 * это на самом деле
 * Created by orantius on 6/19/15.
 */
@Ignore
public class AttributeParamTest extends AttributeParamsImpl {

    private final AttributeParamMeta quantileMeta;
    private final AttributeParamMeta sizeMeta;
    private final AttributeParamMeta ordinalMeta;
    private final AttributeParamMeta colorMeta;
    private final AttributeParamMeta attributionMeta;

    public AttributeParamTest() {
        super(false);

        quantileMeta = new AttributeParamMeta("quantile", "квант",qc->"50",new ParamValidator() {
            private final TIntHashSet quantileValues = new TIntHashSet(Qvalue.quantileValues());
            @Override
            public boolean isValid(String parameter, QueryContext queryContext) {
                try {
                    int parsed = Integer.parseInt(parameter);
                    return quantileValues.contains(parsed);
                } catch (NumberFormatException ignored) {
                    return false;
                }
            }
        },"\\d+", v-> Collections.singletonMap("quantile", e -> ClickHouse.f(Integer.parseInt(v)/100.0)));

        colorMeta = new AttributeParamMeta("currency", "цвет", qc->"Борща", new ParamValidator() {
            private final Set<String> colorValues = Sets.newHashSet("Рыжего", "Борща", "Синеватого");
            @Override
            public boolean isValid(String parameter, QueryContext queryContext) {
                return colorValues.contains(parameter);
            }
        }, ".*", v->Collections.singletonMap("currency", e -> ClickHouse.s(v)));

        attributionMeta = new AttributeParamMeta("attribution", "атрибуция", qc->"last", new ParamValidator() {
            @Override
            public boolean isValid(String parameter, QueryContext queryContext) {
                try {
                    Attribution.valueOf(parameter.toUpperCase());
                    return true;
                } catch (IllegalArgumentException ignored) {
                    return false;
                }
            }
        }, ".*", v->Collections.singletonMap("attribution", e -> ClickHouse.s(v)));

        sizeMeta = new AttributeParamMeta("size", "размер", qc->"42", new ParamValidator() {
            @Override
            public boolean isValid(String parameter, QueryContext queryContext) {
                try {
                    Attribution.valueOf(parameter.toUpperCase());
                    return true;
                } catch (IllegalArgumentException ignored) {
                    return false;
                }
            }
        }, ".*", v->Collections.singletonMap("size", e -> ClickHouse.s(v)));
        ordinalMeta = new AttributeParamMeta("ordinal", "размер", qc->"42", new ParamValidator() {
            @Override
            public boolean isValid(String parameter, QueryContext queryContext) {
                try {
                    Attribution.valueOf(parameter.toUpperCase());
                    return true;
                } catch (IllegalArgumentException ignored) {
                    return false;
                }
            }
        }, ".*", v->Collections.singletonMap("ordinal", e -> ClickHouse.s(v)));


        addMeta(quantileMeta, colorMeta, attributionMeta, sizeMeta, ordinalMeta);
    }

    public AttributeParamMeta getQuantileMeta() {
        return quantileMeta;
    }

    public AttributeParamMeta getSizeMeta() {
        return sizeMeta;
    }

    public AttributeParamMeta getOrdinalMeta() {
        return ordinalMeta;
    }

    public AttributeParamMeta getColorMeta() {
        return colorMeta;
    }

    public AttributeParamMeta getAttributionMeta() {
        return attributionMeta;
    }
}
