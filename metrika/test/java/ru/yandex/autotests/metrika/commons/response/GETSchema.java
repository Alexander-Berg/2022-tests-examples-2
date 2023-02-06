package ru.yandex.autotests.metrika.commons.response;

import org.apache.commons.lang3.builder.EqualsBuilder;
import org.apache.commons.lang3.builder.HashCodeBuilder;
import org.apache.commons.lang3.builder.ToStringBuilder;

/**
 * Created by konkov on 26.10.2016.
 */
public class GETSchema {
    private Long code;
    private String message;

    public Long getCode() {
        return code;
    }

    public void setCode(Long code) {
        this.code = code;
    }

    public GETSchema withCode(Long code) {
        this.code = code;
        return this;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public GETSchema withMessage(String message) {
        this.message = message;
        return this;
    }

    @Override
    public String toString() {
        return ToStringBuilder.reflectionToString(this);
    }

    @Override
    public int hashCode() {
        return new HashCodeBuilder()
                .append(code)
                .append(message)
                .toHashCode();
    }

    @Override
    public boolean equals(Object other) {
        if (other == this) {
            return true;
        }
        if ((other instanceof GETSchema) == false) {
            return false;
        }
        GETSchema rhs = ((GETSchema) other);
        return new EqualsBuilder()
                .append(code, rhs.code)
                .append(message, rhs.message)
                .isEquals();
    }
}
