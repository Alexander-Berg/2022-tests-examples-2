package ru.yandex.autotests.metrika.exceptions;

/**
 * Created by konkov on 18.12.2015.
 */
public class KnownIssueFixedException extends Exception {
    public KnownIssueFixedException(String message) {
        super(message);
    }

    public KnownIssueFixedException(String message, Throwable cause) {
        super(message, cause);
    }

    public KnownIssueFixedException(Throwable cause) {
        super(cause);
    }
}
