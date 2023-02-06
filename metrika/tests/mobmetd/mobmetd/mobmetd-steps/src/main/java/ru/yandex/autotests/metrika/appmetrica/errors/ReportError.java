package ru.yandex.autotests.metrika.appmetrica.errors;

import org.hamcrest.Matcher;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import static org.hamcrest.Matchers.*;

public enum ReportError implements IExpectedError {

    WRONG_START_END_DATE(400, anyOf(
            startsWith("Неверно указана дата начала или дата окончания отчетности"),
            startsWith("Date of beginning or end of accounting period entered incorrectly"))),
    BAD_RETENTION_FILTER(400, equalTo("Retention field is allowed only with 'devices' metric")),
    TOO_MANY_TERMS_IN_FILTERS(400, equalTo("Превышено количество условий в фильтре запроса, значение: 101, лимит: 100, код ошибки: 4021")),
    CONVERSION_FAILED(400, startsWith("Failed to convert property")),
    TOO_COMPLICATED(400, anyOf(
            equalTo("Запрос слишком сложный. Пожалуйста, уменьшите интервал дат или семплирование."),
            equalTo("Query is too complicated. Please reduce the date interval or sampling."))),
    SEGMENT_ATTRIBUTE_NOT_ALLOWED(400, equalTo("Segments attribute is not allowed in subqueries/parameters")),
    ERR_WRONG_ATTRIBUTE(400, startsWith("Неверно указан атрибут")),
    ERR_WRONG_METRIC(400, startsWith("Неверно указана метрика")),
    ERR_WRONG_FILTER(400, startsWith("Неверно указан фильтр для сегментации")),
    WRONG_EXPRESSION(400, startsWith("Неверно указано выражение"));

    private final int code;
    private final Matcher<String> message;

    ReportError(int code, Matcher<String> message) {
        this.code = code;
        this.message = message;
    }

    public Long getCode() {
        return (long) code;
    }

    public Matcher<String> getMessage() {
        return message;
    }

    @Override
    public String toString() {
        return String.format("%s %s", code, message);
    }
}
