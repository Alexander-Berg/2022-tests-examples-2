package ru.yandex.autotests.metrika.exceptions;

/**
 * Created by konkov on 25.03.2015.
 */
public class MetrikaApiWrapperException extends RuntimeException {

    public MetrikaApiWrapperException(String message) {
        super(message);
    }

    public MetrikaApiWrapperException(String message, Throwable cause) {
        super(message, cause);
    }
}
