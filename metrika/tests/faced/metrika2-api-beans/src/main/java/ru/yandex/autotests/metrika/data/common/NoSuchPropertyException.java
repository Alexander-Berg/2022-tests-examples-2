package ru.yandex.autotests.metrika.data.common;

/**
 * Created by vananos on 04.08.16.
 */
public class NoSuchPropertyException extends RuntimeException {

    public NoSuchPropertyException(String message) {
        super(message);
    }
    public NoSuchPropertyException(String message, Throwable cause) {
        super(message, cause);
    }
    public NoSuchPropertyException(Throwable cause) {
        super(cause);
    }
}