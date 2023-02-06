package ru.yandex.autotests.advapi;

import ru.yandex.autotests.metrika.commons.response.CustomError;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import static org.hamcrest.Matchers.*;

public class Errors {

    public static final IExpectedError ACCESS_DENIED = new CustomError(403L, equalTo("Access is denied"));
    public static final IExpectedError SIZE_MUST_BE_BETWEEN = new CustomError(400L, startsWith("размер должен быть между "));
    public static final IExpectedError MUST_BE_LESS_OR_EQUAL = new CustomError(400L, startsWith("должно быть меньше или равно "));
    public static final IExpectedError MUST_BE_GREATER_OR_EQUAL = new CustomError(400L, startsWith("должно быть больше или равно "));
    public static final IExpectedError MAY_NOT_BE_NULL = new CustomError(400L, equalTo("должно быть задано"));
    public static final IExpectedError MAY_NOT_BE_EMPTY = new CustomError(400L, equalTo("не может быть пусто"));
    public static final IExpectedError ADVERTISER_NOT_FOUND = new CustomError(400L, equalTo("Указанный рекламодатель не найден"));
    public static final IExpectedError INCORRECT_PARAMETER_VALUE = new CustomError(400L, equalTo("Неверное значение параметра"));
    public static final IExpectedError QUOTA_EXCEEDED = new CustomError(429L, startsWith("Превышена квота на количество запросов на предоставление гостевого доступа"));
    public static final IExpectedError NOT_FOUND = new CustomError(404L, containsString("not found"));
    public static final IExpectedError LAST_PLACEMENT_REMOVAL = new CustomError(400L, equalTo("the last placement can not be deleted"));
}
