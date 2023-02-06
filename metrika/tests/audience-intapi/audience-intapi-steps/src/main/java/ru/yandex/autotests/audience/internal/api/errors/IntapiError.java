package ru.yandex.autotests.audience.internal.api.errors;

import org.hamcrest.Matcher;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import static org.hamcrest.Matchers.*;

/**
 * Created by ava1on on 09.10.17.
 */
public enum IntapiError implements IExpectedError {
    INVALID_ID(404L, both(startsWith("Object with id = ")).and(endsWith(" not found"))),
    WRONG_SEGMENT_TYPE(400L, both(startsWith("Segment")).and(containsString("is a segment of type")));

    private final Long code;
    private final Matcher<String> message;

    IntapiError(Long code, Matcher<String> message) {
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
}
