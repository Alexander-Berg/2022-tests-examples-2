package ru.yandex.autotests.metrika.errors;

import org.hamcrest.Matcher;
import org.hamcrest.core.IsAnything;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;

/**
 * Created by sourx on 27.05.2016.
 */
public enum AnalyticsReportError implements IExpectedError {

    ANYTING_ERROR(Constants.CODE, new IsAnything<>()),
    OPERATOR_NOT_SUPPORTED_FOR_METRIC(Constants.CODE, equalTo("Operator not supported for metric")),
    OPERATOR_NOT_SUPPORTES_FOR_DIMENSION(Constants.CODE, equalTo("Operator not supported for dimension")),
    VALUE_NOT_SUPPORTED_FOR_METRIC(Constants.CODE, equalTo("Value not supported for metric")),
    TOO_LONG_TERMS(Constants.CODE, equalTo("Too long terms in filters")),
    TOO_MANY_TERMS(Constants.CODE, equalTo("Too many terms in filters")),
    TOO_MANY_ATTRIBUTES(Constants.CODE, equalTo("Too many attributes in filters")),
    WRONG_START_OR_END_DATE(Constants.CODE, equalTo("Wrong start or end date")),
    TYPE_CONVERSION_ERROR(Constants.CODE, startsWith("Type conversion error"));

    private final Long code;
    private final Matcher<String> message;

    AnalyticsReportError(Long code, Matcher<String> message) {
        this.code = code;
        this.message = message;
    }

    public Long getCode() {
        return code;
    }

    public Matcher<String> getMessage() {
        return message;
    }

    @Override
    public String toString() {
        return String.format("%s %s", code, message);
    }

    private static class Constants {
        public static final Long CODE = 400L;
    }
}
