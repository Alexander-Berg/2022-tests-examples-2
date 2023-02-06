package ru.yandex.autotests.metrika.appmetrica.exceptions;

public class AppMetricaException extends RuntimeException {
    public AppMetricaException(String message) {
        super(message);
    }

    public AppMetricaException(String message, Throwable cause) {
        super(message, cause);
    }

    public AppMetricaException(Throwable cause) {
        super(cause);
    }
}
