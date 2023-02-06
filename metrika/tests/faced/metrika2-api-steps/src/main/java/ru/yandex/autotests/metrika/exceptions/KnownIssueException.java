package ru.yandex.autotests.metrika.exceptions;

import org.hamcrest.Matcher;
import org.junit.internal.AssumptionViolatedException;

/**
 * Created by konkov on 09.10.2014.
 */
public class KnownIssueException extends AssumptionViolatedException {
    public KnownIssueException(String assumption, boolean valueMatcher, Object value, Matcher<?> matcher) {
        super(assumption, valueMatcher, value, matcher);
    }

    public KnownIssueException(Object value, Matcher<?> matcher) {
        super(value, matcher);
    }

    public KnownIssueException(String assumption, Object value, Matcher<?> matcher) {
        super(assumption, value, matcher);
    }

    public KnownIssueException(String assumption) {
        super(assumption);
    }

    public KnownIssueException(String assumption, Throwable t) {
        super(assumption, t);
    }
}
