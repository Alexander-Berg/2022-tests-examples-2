package ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc;

import java.util.function.Supplier;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.RandomUtils;

import ru.yandex.autotests.metrika.appmetrica.data.EcomEventType;
import ru.yandex.metrika.api.constructor.response.DimensionMetaExternal;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;
import ru.yandex.metrika.api.constructor.response.ParamMetaExternal;

import static org.apache.commons.lang3.RandomUtils.nextInt;

public enum AttributeParam {
    CURRENCY("currency", AttributeParam::randomCurrency),
    APP_CURRENCY("app_currency", AttributeParam::randomAppCurrency),
    ECOM_TYPE("ecom_type", AttributeParam::randomEcomEventType),
    PARAM_KEY("param_key", AttributeParam::randomParamKey);

    private String paramName;
    private Supplier<String> valueSupplier;

    AttributeParam(String paramName, Supplier<String> valueSupplier) {
        this.paramName = paramName;
        this.valueSupplier = valueSupplier;
    }

    public String getParamName() {
        return paramName;
    }

    public String getRandomValue() {
        return valueSupplier.get();
    }

    public static String getParametrizedDim(DimensionMetaExternal dim) {
        String result = dim.getDim();

        if (dim.getParameter() != null) {
            result = result.replace("<" + dim.getParameter().getId() + ">", getParameterValue(dim.getParameter().getId()));
        }

        return result;
    }

    public static String getParametrizedMetric(MetricMetaExternal metric) {
        String dim = metric.getDim();

        for (ParamMetaExternal parameter : metric.getParameters()) {
            dim = getParametrizedDim(dim, parameter.getId(), getParameterValue(parameter.getId()));
        }

        return dim;
    }

    public static String getParametrizedDim(String dim, String param, String value) {
        return dim.replace("<" + param + ">", value);
    }

    private static String getParameterValue(String paramName) {
        AttributeParam param = getByName(paramName);
        return param.getRandomValue();
    }

    private static AttributeParam getByName(String paramName) {
        return Stream.of(values())
                .filter(param -> param.getParamName().equals(paramName))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("Unexpected param " + paramName));
    }

    private static final ImmutableList<String> CURRENCIES = ImmutableList.of("RUB", "EUR", "USD");

    private static String randomCurrency() {
        return CURRENCIES.get(nextInt(0, CURRENCIES.size()));
    }

    private static String randomAppCurrency() {
        return RandomStringUtils.randomAlphanumeric(RandomUtils.nextInt(1, 10));
    }

    private static String randomEcomEventType() {
        int randomIndex = nextInt(0, EcomEventType.values().length);
        return EcomEventType.values()[randomIndex].getStringValue();
    }

    private static String randomParamKey() {
        return RandomStringUtils.randomAlphanumeric(RandomUtils.nextInt(1, 10));
    }
}
