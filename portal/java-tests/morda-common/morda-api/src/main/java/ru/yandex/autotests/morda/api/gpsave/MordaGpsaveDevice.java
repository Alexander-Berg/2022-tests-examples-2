package ru.yandex.autotests.morda.api.gpsave;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 30/05/16
 */
public enum MordaGpsaveDevice {
    GPS(0),
    WIFI(1),
    GSM(2);

    int value;

    MordaGpsaveDevice(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }
}
