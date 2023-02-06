package ru.yandex.autotests.audience.internal.api.core;

import java.io.IOException;

public class CryptaDeserializerException extends RuntimeException {

    public CryptaDeserializerException(String message, IOException exception) {
        super(message, exception);
    }

    public CryptaDeserializerException(String message) {
        super(message);
    }
}
