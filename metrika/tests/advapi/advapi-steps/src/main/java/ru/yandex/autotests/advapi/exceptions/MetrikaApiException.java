package ru.yandex.autotests.advapi.exceptions;

/**
 * Created by omaz on 14.06.14.
 */
public class MetrikaApiException extends RuntimeException {

    public MetrikaApiException(String err) {
        super(err);
    }

    public MetrikaApiException(String message, Throwable cause) {
        super(message, cause);
    }

}
