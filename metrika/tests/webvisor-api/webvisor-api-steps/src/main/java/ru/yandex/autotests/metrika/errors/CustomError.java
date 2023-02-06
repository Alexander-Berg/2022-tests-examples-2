package ru.yandex.autotests.metrika.errors;

import org.hamcrest.Matcher;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import static org.hamcrest.Matchers.equalTo;

/**
 * Created by konkov on 27.05.2015.
 */
public class CustomError implements IExpectedError {

    private Long code;
    private Matcher<String> message;

    public CustomError(Long code, Matcher<String> message) {
        this.code = code;
        this.message = message;
    }

    public CustomError withCode(final Long code) {
        this.code = code;
        return this;
    }

    public CustomError withMessage(final Matcher<String> message) {
        this.message = message;
        return this;
    }

    public CustomError withMessage(final String message) {
        return withMessage(equalTo(message));
    }

    public CustomError withMessage(final String messageTemplate, Object... params) {
        return withMessage(String.format(messageTemplate, params));
    }

    public static CustomError expect(Long code, Matcher<String> message) {
        return new CustomError(code, message);
    }

    public static CustomError expect(Long code, String message) {
        return error()
                .withCode(code)
                .withMessage(message);
    }

    public static CustomError expect(Long code, String messageTemplate, Object... params) {
        return error()
                .withCode(code)
                .withMessage(messageTemplate, params);
    }

    public static CustomError error() {
        return new CustomError(null, null);
    }

    @Override
    public Long getCode() {
        return code;
    }

    @Override
    public Matcher<String> getMessage() {
        return message;
    }

    @Override
    public String toString() {
        return String.format("%s %s", code, message);
    }
}
