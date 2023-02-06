package ru.yandex.autotests.metrika.errors;

import org.hamcrest.Matcher;

import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import static org.hamcrest.Matchers.equalTo;

public enum LogsApiError implements IExpectedError {
    INVALID_DATE2(400L, equalTo("date2 must be before today")),
    WRONG_PERIOD(400L, equalTo("date1 can't be after date2")),
    TOO_BIG_DATE_INTERVAL(400L, equalTo("Размер запрашивамого лога слишком большой. Пожалуйста, уменьшите интревал дат или очистите старые подготовленные запросы логов")),
    TOO_LONG_FIELDS(400L, equalTo("'fields' parameter can't be longer than 3000 symbols"));

    private final Long code;
    private final Matcher<String> message;

    LogsApiError(Long code, Matcher<String> message) {
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
