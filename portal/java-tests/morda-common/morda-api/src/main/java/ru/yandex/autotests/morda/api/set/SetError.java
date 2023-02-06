package ru.yandex.autotests.morda.api.set;

/**
 * User: asamar
 * Date: 01.11.16
 */
public enum SetError {
    BAD_SK("#error:bad_sk"),
    BAD_LANG("#error:bad_lang"),
    BAD_RETPATH("#error:bad_retpath"),
    NO_BLOCK("#error:no_block"),
    BAD_BLOCK("#error:bad_block");

    private String value;

    SetError(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
