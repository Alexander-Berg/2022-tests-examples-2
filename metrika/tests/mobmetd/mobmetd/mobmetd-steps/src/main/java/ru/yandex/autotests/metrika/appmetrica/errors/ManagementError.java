package ru.yandex.autotests.metrika.appmetrica.errors;

import org.hamcrest.Matcher;

import ru.yandex.autotests.metrika.commons.response.IExpectedError;

import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.irt.testutils.matchers.CompositeMatcher.matchEvery;

/**
 * Created by konkov on 15.09.2016.
 */
public enum ManagementError implements IExpectedError {

    NOT_FOUND(404, matchEvery(startsWith("Object with id = "), endsWith(" not found"))),
    DELETED(404, equalTo("Entity not found")),
    FORBIDDEN(403, not(isEmptyOrNullString())),
    MUST_NOT_BE_NULL(400, equalTo("must not be null")),

    GRANT_DUPLICATE(400, anyOf(equalTo("Разрешение этому пользователю уже выдано. Его можно отредактировать."),
            equalTo("Permission has already been issued to this user. It can be edited."))),
    GRANT_NOT_FOUND(400, allOf(startsWith("У пользователя"), containsString("нет разрешения на счетчик"))),
    TRACKER_NOT_FOUND(404, equalTo("There are no campaigns for given pair (tracking id, API Key)")),

    UID_ALREADY_HAS_ORGANIZATION(409, equalTo("Uid already has organization")),

    APP_EMPTY_TIMEZONE(400, anyOf(equalTo("Не задан часовой пояс приложения"),
            equalTo("App time zone not set"))),
    APP_INVALID_TIMEZONE(400, anyOf(equalTo("Некорректное значение часового пояса"),
            equalTo("Invalid time zone value"))),
    APP_EMPTY_CATEGORY(400, anyOf(equalTo("Не задана категория приложения"),
            equalTo("App category not set"))),

    WIN_INVALID_CREDENTIALS(409, equalTo("Значения не прошли проверку подлинности")),
    ANDROID_INVALID_CREDENTIALS(409, equalTo("Ключ не прошёл проверку подлинности")),
    APPLE_INVALID_CREDENTIALS(409, equalTo("Сертификат не прошёл проверку подлинности")),
    APPLE_DEV_CREDENTIALS(409, equalTo("Пожалуйста, загрузите Production сертификат")),
    HUAWEI_INVALID_CREDENTIALS(409, equalTo("Значения не прошли проверку подлинности")),

    TEST_DEVICE_PUSH_ONLY_PURPOSE_CONFLICT(409, anyOf(
            endsWith("может быть использован только для тестирования push-уведомлений"),
            endsWith("can only be used for testing push notifications"))),

    ACCESS_TO_TRACKER_DENIED(403, equalTo("User haven't access to trackers")),
    INVALID_PARAMETER(400, anyOf(equalTo("Invalid parameter value"), equalTo("Неверное значение параметра"))),
    INVALID_STRICT_ATTR_WINDOW(409, equalTo("Not supported strict attribution window")),
    ADWORDS_DUPLICATE_DEPRECATED(409, anyOf(startsWith("Идентификатор конверсии и ярлык конверсии используются"),
            startsWith("Conversion ID and Conversion Label already used in"))),
    ADWORDS_DUPLICATE(409, anyOf(startsWith("Идентификатор связи используется"),
            startsWith("Link ID already used in"))),
    MANDATORY_POSTBACK(409, allOf(startsWith("Mandatory postbacks "),
            endsWith(" can't be updated"))),
    ENTITY_IS_REFERENCED(409, equalTo("This entity is referenced by another")),
    UNAUTHORIZED(401, equalTo("Неавторизованный пользователь")),

    INVALID_EVENT_NAME(400, anyOf(
            startsWith("Такого события не существует:"),
            startsWith("The event does not exist"))),

    INVALID_DOUBLECLICK_PLATFORM(409, equalTo("Wrong platforms count for doubleclick partner")),
    INVALID_DOUBLECLICK_FINGERPRINT_WINDOW(409, equalTo("Not supported fingerprint attribution window")),
    DOUBLECLICK_EMPTY_CAT(409, anyOf(equalTo("Поле cat не может быть пустым"),
            equalTo("DoubleClick cat field can't be empty"))),

    REMARKETING_TRACKER_MISSING_DEEPLINK(409, equalTo("Remarketing tracker must have a deeplink")),
    REMARKETING_TRACKER_MULTIPLE_PLATFORM(409, equalTo("Remarketing tracker must have single platform")),
    REMARKETING_TRACKER_EDITING(409, equalTo("It is not allowed to edit remarketing settings for a campaign")),

    PROFILE_DUPLICATE(400, anyOf(
            allOf(startsWith("The attribute "), endsWith("already exists. You cannot create two attributes with the " +
                    "same name and type")),
            allOf(startsWith("Атрибут "), endsWith(" уже существует. Нельзя создать два атрибута с одинаковым именем " +
                    "и типом")))),
    PROFILE_ADD_ACTIVE_NAME(400, anyOf(
            allOf(startsWith("The attribute "), endsWith(" is already active. To add the attribute, archive the " +
                    "already active")),
            allOf(startsWith("Атрибут "), endsWith(" уже используется. Чтобы добавить атрибут, отправьте в архив уже " +
                    "используемый")))),
    PROFILE_RESTORE_ACTIVE_NAME(400, anyOf(
            allOf(startsWith("The attribute "), endsWith(" is already active. To restore the attribute, archive the " +
                    "already active")),
            allOf(startsWith("Атрибут "), endsWith(" уже используется. Чтобы восстановить атрибут, отправьте в архив " +
                    "уже используемый")))),

    GRANTS_QUOTA_EXCEEDED(429, anyOf(
            startsWith("Превышена квота на количество запросов на предоставление гостевого доступа для счетчика"),
            startsWith("Exceeded the quota on the number of requests for guest access to the tag"))),

    SYMBOLS_UPLOAD_QUOTA_EXCEEDED(429, anyOf(
            startsWith("Превышена квота на количество запросов к приложению"),
            startsWith("Exceeded the quota on the number of requests to the app")
    )),

    PARTNER_IS_REFERENCED_BY_TRACKERS(409, anyOf(
            equalTo("Невозможно удалить партнёра, который используется в трекерах"),
            equalTo("You can't delete a partner that is used in trackers"))),

    INVALID_SHARED_SECRET(400, anyOf(
            startsWith("Некорректное значение Shared Secret"),
            startsWith("Shared Secret is invalid"))),
    INVALID_GOOGLE_PUBLIC_KEY(400, anyOf(
            startsWith("Некорректное значение публичного ключа"),
            startsWith("Public key is invalid"))),
    GOOGLE_PUBLIC_KEY_REQUIRED(400, anyOf(
            startsWith("Публичный ключ обязателен"),
            startsWith("Public key is required"))),

    CLOUD_ILLEGAL_EXPORT_FIELD(400, startsWith("Illegal client_events fields: unexpected_field. Allowed fields:")),
    CLOUD_DISABLED_CLUSTER(400, allOf(startsWith("Cluster with id "), endsWith(" is not enabled"))),
    CLOUD_EXPORT_INVALID_START_DATE(400, anyOf(
            equalTo("Export start date cannot be less than the application creation date"),
            equalTo("Дата начала экспорта не может быть меньше даты создания приложения"))),
    CLOUD_TABLE_ALREADY_EXISTS(400, equalTo("table_already_exists")),

    CLOUD_ACCOUNT_DUPLICATED(409, anyOf(
            allOf(startsWith("Сервисный аккаунт с идентификатором"), endsWith("уже добавлен")),
            allOf(startsWith("Service account with ID"), endsWith("has already been added")))),
    CLOUD_ACCOUNT_NOT_FOUND_IN_PG(403, anyOf(
            matchEvery(startsWith("Ошибка авторизации в облаке. Cloud auth key with id"), endsWith(" not found")),
            matchEvery(startsWith("Cloud authorization error. Cloud auth key with id"), endsWith(" not found")))),
    CLOUD_INVALID_PRIVATE_KEY(403, anyOf(
            startsWith("Ошибка авторизации в облаке. Invalid private key format of key"),
            startsWith("Cloud authorization error. Invalid private key format of key"))),
    CLOUD_DENIED_VIEWER_ACCOUNT(403, anyOf(
            equalTo("Ошибка авторизации в облаке. Недостаточно прав. Нужен сервисный аккаунт с ролью editor"),
            equalTo("Cloud authorization error. Not enough rights. Need a service account with the editor role"))),
    CLOUD_ACCOUNT_NOT_FOUND_IN_CLOUD(403, anyOf(
            allOf(startsWith("Ошибка авторизации в облаке. UNAUTHENTICATED: Subject"), endsWith("was not found")),
            allOf(startsWith("Cloud authorization error. UNAUTHENTICATED: Subject"), endsWith("was not found")))),
    CLOUD_ACCOUNT_WITHOUT_KEY_IN_CLOUD(403, anyOf(
            allOf(startsWith("Ошибка авторизации в облаке. UNAUTHENTICATED: Key"), endsWith("was not found")),
            allOf(startsWith("Cloud authorization error. UNAUTHENTICATED: Key"), endsWith("was not found")))),
    CLOUD_ACCOUNT_WITHOUT_GRANTS_IN_CLOUD(403, anyOf(
            equalTo("Ошибка авторизации в облаке. PERMISSION_DENIED: Permission denied"),
            equalTo("Cloud authorization error. PERMISSION_DENIED: Permission denied"))),
    CLOUD_ACCOUNT_WITH_REMOVED_FOLDER(403, anyOf(
            equalTo("Ошибка авторизации в облаке. NOT_FOUND: Folder 'removed' was not found"),
            equalTo("Cloud authorization error. NOT_FOUND: Folder 'removed' was not found"))),

    CRASH_ALERT_SETTINGS_ILLEGAL_EMAIL(400, equalTo("must be a well-formed email address")),
    CRASH_ALERT_SETTINGS_RATE_MUST_LESS_1(400, equalTo("must be greater than or equal to 1")),
    CRASH_ALERT_SETTINGS_RATE_MUST_GREATER_100_000_000(400, equalTo("must be less than or equal to 100000000")),
    CRASH_ALERT_SETTINGS_ILLEGAL_EVENT_TYPE(400, startsWith("Illegal event type ")),

    CRASH_EMAIL_CONFIRMATION_TIMEOUT_NOT_EXPIRED(400,
            allOf(startsWith("Email confirmation timeout for app "), endsWith(" not expired"))),

    SKAD_CONVERSION_VALUE_MODEL_NOT_SET(400, startsWith("Required model is not set")),
    SKAD_CONVERSION_VALUE_UNKNOWN_BUNDLE_IDS(400, startsWith("bundle_ids contain unknown values")),

    REVENUE_SETTINGS_DISABLE_ALL_ERROR(400, anyOf(
            equalTo("Нельзя отключить отображение всех данных в отчете по Revenue"),
            equalTo("You can't disable all the data in the Revenue report"))),

    FACEBOOK_DECRYPTION_KEY_CONFLICT(409, anyOf(
            startsWith("Указанный Referrer Decryption Key уже используется"),
            startsWith("This Referrer Decryption Key is already used"))),

    HUAWEI_LINK_ID_CONFLICT(409, anyOf(startsWith("Huawei Link ID уже используется"),
            startsWith("Huawei Link ID is already in use")));

    private final int code;
    private final Matcher<String> message;

    ManagementError(int code, Matcher<String> message) {
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
