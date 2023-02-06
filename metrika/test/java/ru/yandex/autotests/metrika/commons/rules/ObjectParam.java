package ru.yandex.autotests.metrika.commons.rules;

import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;

/**
 * Created by konkov on 18.12.2015.
 */
public class ObjectParam {
    private final String value;

    public ObjectParam(String value) {
        this.value = value;
    }

    public static ObjectParam param(String value) {
        return new ObjectParam(value);
    }

    public String getValue() {
        return value;
    }

    @Override
    public String toString() {
        return value;
    }

    @Override
    public int hashCode() {
        return new HashCodeBuilder().append(value).build();
    }

    @Override
    public boolean equals(Object other) {
        if (other == null) {
            return false;
        }
        if (other == this) {
            return true;
        }
        if (other.getClass() != getClass()) {
            return false;
        }
        ObjectParam rhs = (ObjectParam) other;
        return new EqualsBuilder()
                .append(value, rhs.value)
                .isEquals();

    }
}
