package ru.yandex.autotests.metrika.errors;

import org.hamcrest.Matcher;
import org.hamcrest.core.IsAnything;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.matchers.CompositeMatcher.matchEvery;

/**
 * Created by konkov on 27.05.2015.
 */
public enum ReportError implements IExpectedError {

    UNKNOWN_ERROR(null, not(new IsAnything<>())),
    TOO_MANY_TERMS_IN_FILTERS(Constants.CODE, equalTo("Превышено количество условий в фильтре запроса, значение: 21, лимит: 20, код ошибки: 4021")),
    TOO_MANY_ATTRIBUTES_IN_FILTERS(Constants.CODE, equalTo("Превышено количество атрибутов в фильтре запроса, значение: 21, лимит: 20, код ошибки: 4020")),
    TOO_MANY_VALUES_IN_FILTER(Constants.CODE, matchEvery(startsWith("Превышено количество значений в фильтре запроса, значение: ym:s:pageViews"), endsWith(", код ошибки: 4031"))),
    TOO_MANY_METRICS(Constants.CODE, equalTo("Превышено количество метрик в запросе, значение: 21, лимит: 20, код ошибки: 4015")),
    TOO_MANY_DIMENSIONS(Constants.CODE, equalTo("Превышено количество группировок в запросе, значение: 11, лимит: 10, код ошибки: 4016")),
    METRICS_AND_DIMENSIONS_NOT_ALLOWED_IN_OR(Constants.CODE, equalTo("Оператор OR не может быть использован в фильтре для указанных метрики и группировки, код ошибки: 4010")),
    VISITS_AND_HITS_ONLY_IN_FILTERS(Constants.CODE, matchEvery(startsWith("Метрики и группировки с различными префиксами могут быть использованы совместно только при фильтрации данных, значение:"), endsWith("код ошибки: 4011"))),
    MUST_BE_GREATER_THAN_OR_EQUAL_TO_ZERO(Constants.CODE, equalTo("должно быть больше или равно 0")),
    MULTIPLE_DATESETS_NOT_ALLOWED(Constants.CODE, equalTo("Используется более одного множества в группировках запроса, код ошибки: 4024")),
    WRONG_PARAMETR_URL(Constants.CODE, equalTo("Неверно указан параметр, значение: url parameter is incorrect:null, код ошибки: 4018")),
    DIRECT_CLIENT_LOGINS(Constants.CODE, equalTo("direct_client_logins")),
    OPERATOR_NOT_SUPPORTED_FOR_DIMENSION(Constants.CODE, matchEvery(startsWith("Указанный оператор не поддерживается используемой группировкой, значение:"), endsWith(", код ошибки: 4007"))),
    OPERATOR_NOT_SUPPORTED_FOR_METRIC(Constants.CODE, matchEvery(startsWith("Указанный оператор не поддерживается используемой метрикой, значение:"), endsWith(", код ошибки: 4006"))),
    NO_OBJECT_ID(Constants.CODE, equalTo("Нет объекта с указанным ID.")),
    VALUE_NOT_SUPPORTED_FOR_DIMENSION(Constants.CODE, matchEvery(startsWith("Указанное значение не поддерживается используемой группировкой, значение:"), endsWith("код ошибки: 4009"))),
    WRONG_ACCURACY_FORMAT(Constants.CODE, equalTo("Некорректный коэффициент семплирования")),
    WRONG_LANG(Constants.CODE, equalTo("Неверное значение параметра языка")),
    INVALID_PARAMETER(Constants.CODE, equalTo("Неверно задан параметр")),
    WRONG_ATTRIBUTE(Constants.CODE, matchEvery(startsWith("Неверно указан фильтр для сегментации, значение: Фильтр по метрике не поддерживается:"), endsWith(", код ошибки: 4003"))),
    TOO_LONG_TERMS_IN_FILTERS(Constants.CODE, matchEvery(startsWith("Некоторые условия в фильтре запроса слишком длинные, значение:"), containsString(", лимит:"), endsWith(", код ошибки: 4022"))),
    TOO_MANY_KEYS_IN_ROW_IDS(Constants.CODE, matchEvery(startsWith("Превышено количество ключей, значение: "), containsString(", лимит:"), endsWith(", код ошибки: 4025"))),
    TOO_MANY_DIMENSIONS_IN_ROW_IDS(Constants.CODE, matchEvery(startsWith("Превышено количество группировок в ключе, номер:"), containsString(", значение:"), containsString(", лимит:"), endsWith(", код ошибки: 4026"))),
    WRONG_PARAMETER_ROWIDS(Constants.CODE, startsWith("Wrong parameter: 'row_ids', value: ")),
    RESTRICTED(Constants.ACCESS_DENIED, matchEvery(startsWith("Нет доступа, значение:"), endsWith(", код ошибки: 4019"))),
    WRONG_ATTRIBUTE_REAL(Constants.CODE, matchEvery(startsWith("Неверно указан атрибут, значение: "), endsWith(", код ошибки: 4001"))),
    WRONG_METRIC(Constants.CODE, matchEvery(startsWith("Неверно указана метрика, значение:"), endsWith(", код ошибки: 4002"))),
    WRONG_FILTER(Constants.CODE, matchEvery(startsWith("Неверно указан фильтр для сегментации, значение:"), endsWith(", код ошибки: 4003"))),
    WRONG_REGEXP(Constants.CODE, startsWith("wrong regexp")),
    WRONG_EXPRESSION(Constants.CODE, matchEvery(startsWith("Неверно указано выражение, значение:"), endsWith(", код ошибки: 4036"))),
    WRONG_TIME_INTERVAL(Constants.CODE, matchEvery(startsWith("Неправильный интервал времени в паттерне, значение:"), endsWith(", код ошибки: 4030"))),
    INTERVAL_TOO_BIG(Constants.CODE, matchEvery(startsWith("Слишком большой интервал времени в паттерне, значение:"), endsWith(", код ошибки: 4028"))),
    TOO_MANY_CONDITIONS(Constants.CODE, matchEvery(startsWith("Слишком много условий в паттерне, значение:"), endsWith(", код ошибки: 4029"))),
    UNSUPPORTED_METRIC_VALUE(Constants.CODE, matchEvery(startsWith("Указанное значение не поддерживается используемой метрикой,"), endsWith("код ошибки: 4008"))),
    WRONG_FILTER_SEGMENT_A(Constants.CODE, matchEvery(startsWith("Неверно указан фильтр для сравнения A, значение:"), endsWith(", код ошибки: 4033"))),
    WRONG_FILTER_SEGMENT_B(Constants.CODE, matchEvery(startsWith("Неверно указан фильтр для сравнения B, значение:"), endsWith(", код ошибки: 4034"))),
    METRICS_AND_DIMENSIONS_NOT_ALLOWED_IN_OR_WITH_VALUE(Constants.CODE, matchEvery(startsWith("Оператор OR не может быть использован в фильтре для указанных метрики и группировки, значение:"), endsWith(", код ошибки: 4010"))),
    SEGMENT_METRICS_AND_DIMENSIONS_NOT_ALLOWED_IN_OR(Constants.CODE, matchEvery(startsWith("Оператор OR не может быть использован в фильтре для указанных метрики и группировки, значение:"), endsWith(", код ошибки: 4010"))),
    WRONG_START_OR_END_DATE(Constants.CODE, matchEvery(startsWith("Неверно указана дата начала или дата окончания отчетности, значение:"), endsWith(", код ошибки: 4005"))),
    MUST_BE_GREATER_THAN_OR_EQUAL_TO_1(Constants.CODE, equalTo("должно быть больше или равно 1")),
    WRONG_LIMIT(Constants.CODE, matchEvery(startsWith("Неправильное значение параметра limit, значение:"), endsWith(", код ошибки: 4013"))),
    WRONG_ATTRIBUTION_VALUE(Constants.CODE, startsWith("Wrong attribution value:")),
    WRONG_PARAM_DATE(Constants.CODE, matchEvery(startsWith("Неверно указан параметр, значение:"), endsWith("код ошибки: 4018"))),
    WRONG_PARAM_NAME(Constants.CODE, startsWith("Invalid property")),
    INCORRECT_VISIT_RU(Constants.CODE, startsWith("Некорректный визит "));

    private final Long code;
    private final Matcher<String> message;

    ReportError(Long code, Matcher<String> message) {
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
        public static final long CODE = 400L;
        public static final long ACCESS_DENIED = 403l;
    }
}
