package ru.yandex.autotests.metrika.data.metadata.v1;

import ch.lambdaj.function.convert.StringConverter;
import org.apache.commons.lang.StringUtils;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.report.v1.enums.GroupEnum;
import ru.yandex.metrika.segments.site.parametrization.Attribution;

import java.util.HashMap;
import java.util.Map;

import static ru.yandex.autotests.metrika.data.common.counters.Counter.EXPERIMENT_ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.GOAL_ID;

/**
 * Created by konkov on 27.11.2014.
 * <p/>
 * Набор значений параметров для параметризованных метрик и измерений.
 * Может использоваться для подстановки в наименованиях, либо для передачи
 * непосредственнов  в запросах.
 */
public class ParameterValues extends HashMap<ParametrizationTypeEnum, String> {

    private static final int DEFAULT_QUANTILE = 50;
    private static final String DEFAULT_CURRENCY = "RUB";
    private static final GroupEnum DEFAULT_GROUP = GroupEnum.DAY;
    private static final Attribution DEFAULT_ATTRIBUTION = Attribution.LAST;
    private static final int DEFAULT_EXPERIMENT = 6;

    public static final ParameterValues EMPTY = new ParameterValues();

    public static ParameterValues getDefaults(Counter counter) {
        return new ParameterValues()
                .append(ParametrizationTypeEnum.ATTRIBUTION, DEFAULT_ATTRIBUTION.name().toLowerCase())
                .append(ParametrizationTypeEnum.GOAL_ID, String.valueOf(counter.get(GOAL_ID)))
                .append(ParametrizationTypeEnum.GROUP, DEFAULT_GROUP.getValue())
                .append(ParametrizationTypeEnum.QUANTILE, String.valueOf(DEFAULT_QUANTILE))
                .append(ParametrizationTypeEnum.CURRENCY, DEFAULT_CURRENCY)
                .append(ParametrizationTypeEnum.EXPERIMENT, counter.getProperties().contains(EXPERIMENT_ID) ?
                        String.valueOf(counter.get(EXPERIMENT_ID)) :
                        String.valueOf(DEFAULT_EXPERIMENT));
    }

    public ParameterValues append(ParametrizationTypeEnum key, String value) {
        put(key, value);
        return this;
    }

    public IFormParameters toFormParameters() {
        FreeFormParameters result = new FreeFormParameters();
        for (Map.Entry<ParametrizationTypeEnum, String> entry : entrySet()) {
            result.put(entry.getKey().getParameterName(), entry.getValue());
        }
        return result;
    }

    public String substitute(String parameterized) {
        String replaced = parameterized;
        if (StringUtils.isNotEmpty(replaced)) {
            for (Map.Entry<ParametrizationTypeEnum, String> entry : entrySet()) {
                replaced = replaced.replace(entry.getKey().getPlaceholder(), entry.getValue());
            }
        }
        return replaced;
    }

    public StringConverter<String> getSubstitute() {
        return new StringConverter<String>() {
            @Override
            public String convert(String s) {
                return substitute(s);
            }
        };
    }

    public ParameterValues append(ParameterValues other) {
        for (Map.Entry<ParametrizationTypeEnum, String> entry : other.entrySet()) {
            put(entry.getKey(), entry.getValue());
        }

        return this;
    }

}
