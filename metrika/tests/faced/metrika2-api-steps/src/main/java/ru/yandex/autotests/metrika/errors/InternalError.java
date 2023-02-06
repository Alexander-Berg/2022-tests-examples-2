package ru.yandex.autotests.metrika.errors;

import org.hamcrest.Matcher;
import org.hamcrest.core.IsAnything;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import static org.hamcrest.Matchers.*;

/**
 * Created by sourx on 21.07.16.
 */
public enum InternalError implements IExpectedError {
    UNKNOWN_ERROR(null, not(new IsAnything<>())),
    TOO_LONG_TITLE(400L, equalTo("Too long title")),
    TOO_LONG_BODY(400L, equalTo("Too long body")),
    TITLE_SIZE_MUST_BE_MORE_NULL(400L, equalTo("Title's size must be more than 0")),
    INVALID_START_DATE_FORMAT(400L, equalTo("Invalid start_date format")),
    DATE1_MORE_THAN_DATE2(400L, equalTo("date1 more than date2")),
    INVALID_DATE1_FORMAT(400L, equalTo("Invalid date1 format, yyyy-MM-dd expected")),
    INVALID_DATE2_FORMAT(400L, equalTo("Invalid date2 format, yyyy-MM-dd expected"));

    private final Long code;
    private final Matcher<String> message;

    InternalError(Long code, Matcher<String> message) {
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

