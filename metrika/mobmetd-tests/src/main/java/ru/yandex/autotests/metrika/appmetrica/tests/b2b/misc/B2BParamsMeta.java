package ru.yandex.autotests.metrika.appmetrica.tests.b2b.misc;

import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import ru.yandex.metrika.api.constructor.response.DimensionMetaExternal;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;

public class B2BParamsMeta {

    private final DimensionMetaExternal dimension;
    private final MetricMetaExternal metric;

    public B2BParamsMeta(DimensionMetaExternal dimension, MetricMetaExternal metric) {
        this.dimension = dimension;
        this.metric = metric;
    }

    public MetricMetaExternal getMetric() {
        return metric;
    }

    public DimensionMetaExternal getDimension() {
        return dimension;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }

        B2BParamsMeta params = (B2BParamsMeta) o;

        return new EqualsBuilder()
                .append(metric, params.metric)
                .append(dimension, params.dimension)
                .isEquals();
    }

    @Override
    public int hashCode() {
        return new HashCodeBuilder(17, 37)
                .append(metric)
                .append(dimension)
                .toHashCode();
    }
}
