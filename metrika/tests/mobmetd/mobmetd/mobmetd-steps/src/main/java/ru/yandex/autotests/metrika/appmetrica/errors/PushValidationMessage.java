package ru.yandex.autotests.metrika.appmetrica.errors;

public enum PushValidationMessage {
    REQUIRED_FIELD_IS_EMPTY("Обязательное поле не может быть пустым"),
    FIELD_LENGTH_EXCEED("Превышена длина поля"),
    UNSUPPORTED_SILENT_PLATFORM("Отправка push-уведомлений без вывода сообщений (Silent Push Notifications) " +
            "поддерживается только для платформ iOS и Android"),
    ILLEGAL_FIELD_VALUE("Недопустимое значение поля"),
    ANDROID_IMAGE_LINK_ERROR("В поле должна содержаться ссылка на доступное изображение. " +
            "Поддерживаемые протоколы: HTTP, HTTPS."),
    PAYLOAD_LIMIT_EXCEEDED("Размер сообщения превышает допустимый лимит"),
    INVALID_CERT("Неверный сертификат");

    private String message;

    PushValidationMessage(String message) {
        this.message = message;
    }

    public String message() {
        return message;
    }
}
