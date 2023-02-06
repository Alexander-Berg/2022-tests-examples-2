package ru.yandex.qatools.monitoring;

import org.junit.AssumptionViolatedException;
import org.junit.runner.Description;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24/11/16
 */
public class TestCaseResult {
    private Status status;
    private Description description;
    private Throwable error;

    protected TestCaseResult(Status status, Description description) {
        this(status, description, null);
    }

    protected TestCaseResult(Status status, Description description, Throwable error) {
        this.status = status;
        this.description = description;
        this.error = error;
    }

    public static TestCaseResult passed(Description description) {
        return new TestCaseResult(Status.PASSED, description);
    }

    public static TestCaseResult failed(Throwable error, Description description) {
        if (error instanceof AssertionError) {
            return new TestCaseResult(Status.FAILED, description, error);
        }
        return new TestCaseResult(Status.BROKEN, description, error);
    }

    public static TestCaseResult skipped(AssumptionViolatedException error, Description description) {
        return new TestCaseResult(Status.SKIPPED, description, error);
    }

    public Status getStatus() {
        return status;
    }

    public Description getDescription() {
        return description;
    }

    public Throwable getError() {
        return error;
    }

    public enum Status {
        PASSED,
        FAILED,
        BROKEN,
        SKIPPED
    }
}
