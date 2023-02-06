package ru.yandex.autotests.audience.internal.api.data;

/**
 * Created by ava1on on 07.08.17.
 */
public enum GoalSubtype {
    UPLOADING_EMAIL("uploading_email"),
    UPLOADING_PHONE("uploading_phone"),
    UPLOADING_IDFA_GAID("uploading_idfa_gaid"),
    UPLOADING_YUID("uploading_yuid"),
    UPLOADING_CLIENT_ID("uploading_client_id"),
    UPLOADING_MAC("uploading_mac"),
    UPLOADING_CRM("uploading_crm"),
    METRIKA_COUNTER("metrika_counter_id"),
    METRIKA_SEGMENT("metrika_segment_id"),
    METRIKA_GOAL("metrika_goal_id"),
    APPMETRICA_APP("appmetrica_api_key"),
    APPMETRICA_SEGMENT("appmetrica_segment_id"),
    GEO_REGULAR("geo_regular"),
    GEO_LAST("geo_last"),
    GEO_CONDITION("geo_condition"),
    GEO_WORK("geo_work"),
    GEO_HOME("geo_home"),
    LOOKALIKE("lookalike"),
    PIXEL("pixel");

    private final String value;

    private GoalSubtype(String value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return this.value;
    }
}
