package ru.yandex.autotests.internalapid.matchers;

import org.hamcrest.Matcher;

import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.startsWith;

/**
 * @author zgmnkv
 */
public enum CommonError implements IExpectedError {

    MUST_BE_GREATER_THAN_OR_EQUAL_TO(400L, startsWith("должно быть больше или равно")),
    MUST_BE_LESS_THAN_OR_EQUAL_TO(400L, startsWith("должно быть меньше или равно")),
    MAY_NOT_BE_EMPTY(400L, endsWith("не может быть пусто")),
    MAY_NOT_BE_NULL(400L, endsWith("должно быть задано")),
    SIZE_MUST_BE_BETWEEN(400L, startsWith("размер должен быть между")),
    EMAIL_NOT_BE_EMPTY(400L, startsWith("email не может быть пустым")),
    INCORRECT_EMAIL(400L, startsWith("email определен в неверном формате")),
    NOT_FOUND(404L, both(startsWith("Object with id = ")).and(endsWith(" not found")).or(equalTo("Entity not found"))),
    NO_OBJECT_ID(400L, equalTo("Нет объекта с указанным ID.")),
    MUST_BE_GREATER_THAN_OR_EQUAL_TO_1(400L, equalTo("должно быть больше или равно 1"));


    private final Long code;
    private final Matcher<String> message;

    CommonError(Long code, Matcher<String> message) {
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
