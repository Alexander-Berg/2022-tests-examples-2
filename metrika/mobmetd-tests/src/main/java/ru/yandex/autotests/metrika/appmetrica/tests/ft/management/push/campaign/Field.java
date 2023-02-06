package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.push.campaign;

public enum Field {
    TEXT("text"),
    TITLE("title"),
    ICON("icon"),
    ICON_BACKGROUND("icon_background"),
    IMAGE("image"),
    DATA("data"),
    SOUND("sound"),
    MUTABLE_CONTENT("mutable_content"),
    CATEGORY("category"),
    THREAD_ID("thread_id"),
    APNS_COLLAPSE_ID("collapse_id"),
    VIBRATION("vibration"),
    LED_COLOR("led_color"),
    LED_INTERVAL("led_interval"),
    LED_PAUSE_INTERVAL("led_pause_interval"),
    TIME_TO_LIVE("time_to_live"),
    COLLAPSE_KEY("collapse_key"),
    CHANNEL_ID("channel_id"),
    PRIORITY("priority"),
    URGENCY("urgency"),
    BANNER("banner"),
    BADGE("badge"),
    EXPIRATION("expiration"),
    ATTACHMENTS("attachments"),
    IGNORED(null);

    private final String fieldName;

    Field(String fieldName) {
        this.fieldName = fieldName;
    }

    public String getFieldName() {
        return fieldName;
    }
}
