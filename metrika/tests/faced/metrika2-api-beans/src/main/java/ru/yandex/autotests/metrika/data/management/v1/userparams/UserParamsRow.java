package ru.yandex.autotests.metrika.data.management.v1.userparams;

import static java.lang.String.format;

/**
 * Created by konkov on 14.04.2016.
 */
public class UserParamsRow {
    private String userId;
    private String key;
    private String value;

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getKey() {
        return key;
    }

    public void setKey(String key) {
        this.key = key;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public UserParamsRow withUserId(final String userId) {
        this.userId = userId;
        return this;
    }

    public UserParamsRow withKey(final String key) {
        this.key = key;
        return this;
    }

    public UserParamsRow withValue(final String value) {
        this.value = value;
        return this;
    }

    @Override
    public String toString() {
        return format("\"%s\",\"%s\",\"%s\"", userId, key, value);
    }
}
