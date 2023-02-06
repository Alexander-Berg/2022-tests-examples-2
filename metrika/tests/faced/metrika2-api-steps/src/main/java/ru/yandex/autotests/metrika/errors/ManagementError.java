package ru.yandex.autotests.metrika.errors;

import org.hamcrest.Matcher;
import org.hamcrest.core.IsAnything;

import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.users.User;

import static org.hamcrest.Matchers.both;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;

/**
 * Created by konkov on 25.11.2014.
 *
 * Ожидаемые в тестах API управления ошибки
 */
public enum ManagementError implements IExpectedError {

    UNKNOWN_ERROR(null, not(new IsAnything<>())),
    UNAUTHORIZED(401L, equalTo("Неавторизованный пользователь")),
    USER_NOT_FOUND_EN(400L, equalTo("User does not exist.")),
    USER_NOT_FOUND_RU(400L, equalTo("Такой пользователь не существует.")),
    ACCESS_DENIED(403L, equalTo("Access is denied")),
    NO_ACCESS_TO_ATTRIBUTE(403L, both(startsWith("Нет доступа, значение:")).and(endsWith("код ошибки: 4019"))),
    INVALID_TOKEN(403L, equalTo("Invalid oauth_token")),
    SEGMENT_ALREADY_EXISTS(400L, equalTo("Сегмент с таким именем уже существует.")),
    INVALID_LENGTH(400L, equalTo("размер должен быть между 1 и 255")),
    WRONG_ATTRIBUTE(400L, startsWith("Неверно указан атрибут,")),
    COUNTER_LIMIT_FOR_LABEL_EXCEEDED(400L, equalTo("Превышен лимит счетчиков для одной метки")),
    INVALID_SITE(400L, equalTo("Неверное доменное имя сайта")),
    INVALID_SITE_ONLY_DOMAIN(400L, startsWith("Укажите домен или полный путь сайта. Статистика будет собираться с тех страниц сайта, на которых установлен код счётчика.")),
    NOT_FOUND(404L, both(startsWith("Object with id = ")).and(endsWith(" not found")).or(equalTo("Entity not found"))),
    CONDITIONS_LIMIT(400L, equalTo("Превышен лимит условий для цели.")),
    GOALS_LIMIT(400L, equalTo("Превышен лимит целей.")),
    CONDITION_URL_LENGTH_LIMIT(400L, equalTo("Слишком длинное условие цели.")),
    CONDITION_URL_EMPTY(400L, equalTo("Условие должно быть не пустым.")),
    INVALID_GOAL_CONDITION(400L, startsWith("Неверно настроена цель")),
    CAN_NOT_BE_EMPTY_CONDITION_URL(400L, startsWith("Не может быть пустым для условия с типом")),
    INVALID_FIRST_FILTER(400L, startsWith("Неверно настроен фильтр '1'")),
    INVALID_REFERER_FILTER(400L, startsWith("Реферер не может быть использован в качестве условия фильтрации")),
    INVALID_IP_FILTER(400L, startsWith("Для фильтра «IP» неверно указано отношение.")),
    INVALID_UNIQ_ID_FILTER(400L, startsWith("Для фильтра «Не учитывать меня» тип фильтра указан неверно.")),
    INVALID_GOAL_TYPE(400L, startsWith("Недопустимый тип цели.")),
    INVALID_MESSENGER_GOAL_CONDITIONS(400L, equalTo("Выберите условие \"Все мессенджеры\" или один конкретный мессенджер")),
    INVALID_MESSENGER_GOAL_WITH_NO_CONDITIONS(400L, equalTo("Цель \"Переход в мессенджер\" должна иметь хотя бы одно условие достижения")),
    INVALID_SOCIAL_NETWORK_GOAL_CONDITIONS(400L, equalTo("Выберите условие \"Все социальные сети\" или одну конкретную социальную сеть")),
    INVALID_SOCIAL_NETWORK_GOAL_WITH_NO_CONDITIONS(400L, equalTo("Цель \"Переход в социальные сети\" должна иметь хотя бы одно условие достижения")),
    PAYMENT_SYSTEM_GOAL_ALREADY_EXIST(400L, equalTo("Цель с типом payment_system уже существует для счетчика.")),
    INVALID_FILE_GOAL_WITH_NO_CONDITIONS(400L, equalTo("Цель \"Скачивание файла\" должна иметь хотя бы одно условие достижения")),
    INVALID_FILE_GOAL_CONDITIONS(400L, equalTo("Выберите условие \"Любой файл\" или один конкретный файл")),
    INVALID_FILE_GOAL_WITH_CONDITION_TYPE_ALL_FILES_AND_WITH_NOT_EMPTY_CONDITION_URL(400L, equalTo("Должно быть пустым для типа all_files")),
    INVALID_BUTTON_GOAL_WITH_NO_CONDITIONS(400L, equalTo("Цель \"Скачивание файла\" должна иметь хотя бы одно условие достижения")),
    INVALID_SITE_SEARCH_GOAL_WITH_NO_CONDITIONS(400L, equalTo("Цель \"Поиск по сайту\" должна иметь хотя бы одно условие достижения")),
    SITE_SEARCH_GOAL_SHOULD_HAS_EXACTLY_ONE_GOAL_CONDITION(400L, equalTo("Ровно одно условие должно быть у цели \"Поиск по сайту\"")),
    FILTERS_LIMIT(400L, equalTo("Превышен лимит фильтров.")),
    OPERATIONS_LIMIT(400L, equalTo("Превышен лимит операций.")),
    WRONG_LOGIN(400L, equalTo("Указан неверный логин.")),
    WEBVISOR_URLS_LIST_TOO_LARGE(400L, equalTo("Слишком длинный список URL-адресов страниц")),
    ECOMMERCE_OBJECT_SIZE(400L, equalTo("размер должен быть между 0 и 200")),
    NO_OBJECT_ID(400L, equalTo("Нет объекта с указанным ID.")),
    LABEL_ALREADY_EXIST(409L, equalTo("Метка с таким именем уже существует.")),
    LABEL_NAME_TOO_LONG(400L, equalTo("Слишком длинная метка.")),
    USER_IS_ALREADY_OWNER(400L, equalTo("Указанный пользователь уже является владельцем счетчика.")),
    UNABLE_MOVE_TO_YANDEX_WITH_DIRECT_ALLOW_USE_GOALS_WITHOUT_ACCESS(400L, equalTo("Для переноса счётчика на служебный логин снимите флаг \"Разрешить в рекламных кампаниях оптимизацию по целям без доступа к счетчику\" на списке целей.")),
    COUNTERS_MAX_COUNT_EXCEEDED(400L, equalTo("Достигнуто максимальное количество счетчиков на аккаунте. Используйте другой аккаунт для новых счетчиков")),
    INVALID_CURRENCY_CODE(400L, startsWith("Неверный код валюты")),
    ACCESS_DENIED_TO_ANOTHER_SEGMENT_TYPE(403L, equalTo("Сегмент принадлежит другому источнику")),
    NOT_ENOUGH_MONEY(400L, equalTo("Необходимо пополнить счет.")),
    NO_RIGHTS_FOR_TRACK_DELETION(403L, equalTo("Нет прав на удаление трека.")),
    NO_RIGHTS_FOR_TRACK_EDITING(403L, equalTo("Нет прав на редактирование трека.")),
    INVALID_UPLOADING(400L, startsWith("Неверный формат данных, ошибка в строке номер")),
    INVALID_MULTIPART_REQUEST(400L, startsWith("Некорректный формат multipart запроса.")),
    MISSING_REQUEST_PART(400L, startsWith("Не найден параметр запроса.")),
    YA_METRIKA_COUNTER_GRANT_ERROR(400L, startsWith("Доступ на счетчики, принадлежащие ya-metrika, adinside или yastorepublisher, выдаётся только через IDM.")),
    GRANTS_QUOTA_EXCEEDING(429L,startsWith("Превышена квота на количество запросов на предоставление гостевого доступа для счетчика")),
    DELEGATE_QUOTA_EXCEEDING(429L, startsWith("Превышена квота на количество запросов на добавление представителя для пользователя")),
    USER_QUOTA_EXCEEDING(429L,startsWith("Превышена квота на количество")),
    COUNTER_QUOTA_EXCEEDING(429L,startsWith("Превышена квота на количество запросов к счётчику")),
    COUNTER_ALREADY_EXISTS(400L, both(startsWith("Счётчик с таким названием и доменом уже существует.")).and(endsWith("Укажите другое наименование."))),
    COUNTER_DOESNT_EXIST(400L, startsWith("Такого счётчика не существует.")),
    WRONG_TIME_ZONE(400L, startsWith("Неверная таймзона:")),
    MISSED_QUERY_PARAMETER(400L, both(startsWith("Required request parameter ")).and(endsWith(" is not present"))),
    WRONG_PARAMETER_VALUE(400L, startsWith("Wrong parameter value")),
    EMPTY_FILE(400L, equalTo("The file is empty")),
    WRONG_COUNTER(400L, startsWith("wrong counter id")),
    PARTNER_DELETE_ERROR(400L, startsWith("can't delete partner counter")),
    COMPOSITE_GOAL_DEFAULT_PRICE_IS_FIXED(400L, startsWith("Нельзя устанавливать значение цены по умолчанию для составной цели.")),
    EMPTY_GOAL_NAME(400L, equalTo("Имя цели не должно быть пустым")),
    EMPTY_GOAL_CONDITION(400L, equalTo("Количество условий должно быть больше нуля")),
    NOT_VALID_GOAL_CONDITION(400L, both(startsWith("Цель")).and(containsString("не может иметь условие типа"))),
    VISIT_JOIN_THRESHOLD_UNMET(400L, startsWith("Загрузить данные сейчас невозможно. Загрузка станет доступна ")),
    MISSED_MANDATORY_COLUMN(400L, startsWith("Отсутствует обязательная колонка ")),
    INCORRECT_VALUE_IN_COLUMN(400L, startsWith("Некорректное значение ")),
    SUBSCRIPTION_COUNTER_IDS_ONLY_FOR_LIST(400L, equalTo("You can't pass counterIds for non SubscriptionListType.LIST")),
    SUBSCRIPTION_LIST_ONLY_FOR_COUNTER_ADVICES(400L, equalTo("Only COUNTER_ADVICES support all possible SubscriptionListType values")),
    SUBSCRIPTION_NOT_ALL_FOR_COUNTER_ADVICES(400L, equalTo("For COUNTER_ADVICES you should specify SubscriptionListType different from ALL")),
    NOT_ALLOWED_SYMBOLS_IN_COUNTER_NAME(400L, equalTo("Наименование счётчика содержит недопустимые символы")),
    NOT_ALLOWED_SYMBOLS_IN_CONDITION_VALUE(400L, equalTo("Значение содержит недопустимые символы.")),
    NOT_ALLOWED_SYMBOLS_IN_ANNOTATION_TITLE(400L, equalTo("Заголовок примечания содержит недопустимые символы.")),
    NOT_ALLOWED_SYMBOLS_IN_ANNOTATION_MESSAGE(400L, equalTo("Описание примечания содержит недопустимые символы.")),
    NOT_ALLOWED_SYMBOLS_IN_COMMENT(400L, equalTo("Комментарий содержит недопустимые символы.")),
    NOT_ALLOWED_SYMBOLS_IN_FILTER_VALUE(400L, equalTo("Значение фильтра содержит недопустимые символы.")),
    NOT_ALLOWED_SYMBOLS_IN_GOAL_NAME(400L, equalTo("Название цели содержит недопустимые символы.")),
    NOT_ALLOWED_SYMBOLS_IN_LABEL_NAME(400L, equalTo("Имя метки содержит недопустимые символы.")),
    NOT_ALLOWED_SYMBOLS_IN_OPERATION_VALUE(400L, equalTo("Значение для замены содержит недопустимые символы.")),
    NOT_ALLOWED_SYMBOLS_IN_SEGMENT_NAME(400L, equalTo("Название сегмента содержит недопустимые символы.")),
    NOT_ALLOWED_SYMBOLS_IN_WEBVISOR_OPTIONS_URLS(400L, equalTo("Список страниц для сохранения содержит недопустимые символы.")),
    FEATURE_CANT_BE_ENABLED(400L, endsWith("фичи нельзя включать через апи")),
    SIZE_MUST_BE_BETWEEN(400L, startsWith("размер должен быть между")),
    CONDITION_TYPE_DOES_NOT_SPECIFIED(400L, equalTo("Не указан тип условия")),
    WRONG_ROBOTS(400L, equalTo("возможные значения: 1 или 2")),
    TELEGRAM_REPORT_EMPTY_SELECTED_METRICS(400L, equalTo(""));

    public static IExpectedError OFFER_NOT_ACCEPTED(User user){
        return new CustomError(400L, equalTo(user.get(LOGIN)));
    }

    private final Long code;
    private final Matcher<String> message;

    ManagementError(Long code, Matcher<String> message) {
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
