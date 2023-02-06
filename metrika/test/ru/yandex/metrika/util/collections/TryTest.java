package ru.yandex.metrika.util.collections;

import java.util.concurrent.Callable;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.runners.MockitoJUnitRunner;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.reset;

@RunWith(MockitoJUnitRunner.class)
public class TryTest {

    private static final String EXCEPTION_MESSAGE = "fail";
    private static final Integer EXPECTED_RESULT = 5;

    @Mock
    private Callable<Integer> failingCallable;

    @Before
    public void setUp() throws Exception {
        makeCallableFailForTwoFirstTimesOnly();
    }

    @Test
    public void throwsExceptionWhenFailedWithOneTryAndSleepTime() {
        assertThatThrownBy(() -> Try.retry(failingCallable, 1, 0))
                .hasMessageEndingWith(EXCEPTION_MESSAGE);
    }

    @Test
    public void throwsExceptionWhenFailedWithOneTry() {
        assertThatThrownBy(() -> Try.retry(failingCallable, 1))
                .hasMessageEndingWith(EXCEPTION_MESSAGE);
    }

    @Test
    public void successfullyExecutesWhenFailedAfterTwoFailuresWithSleepTime() throws Exception {
        assertThat(Try.retry(failingCallable, 3, 0)).isSameAs(EXPECTED_RESULT);
    }

    @Test
    public void successfullyExecutesWhenFailedAfterTwoFailures() throws Exception {
        assertThat(Try.retry(failingCallable, 3)).isSameAs(EXPECTED_RESULT);
    }

    @Test
    public void throwsExceptionExecutesWhenFailedWithUnRetryableException() throws Exception {
        Class<? extends Exception> anotherExpectedException = new RuntimeException() {
        }.getClass();
        assertThatThrownBy(() -> Try.retry(failingCallable, 3, anotherExpectedException::isInstance))
                .hasMessageEndingWith(EXCEPTION_MESSAGE);
    }

    @Test
    public void successfullyExecutesWhenFailedAfterTwoRetryableFailures() throws Exception {
        assertThat(Try.retry(failingCallable, 3, (e) -> e instanceof ExpectedException)).isSameAs(EXPECTED_RESULT);
    }

    @Test
    public void throwsExceptionWhenFailedWithOneTryForRetryableException() {
        assertThatThrownBy(() -> Try.retry(failingCallable, 1, (e) -> e instanceof ExpectedException))
                .hasMessageEndingWith(EXCEPTION_MESSAGE);
    }

    private void makeCallableFailForTwoFirstTimesOnly() throws Exception {
        reset(failingCallable);
        doThrow(new ExpectedException(EXCEPTION_MESSAGE))
                .doThrow(new ExpectedException(EXCEPTION_MESSAGE))
                .doReturn(EXPECTED_RESULT)
                .when(failingCallable).call();
    }

    private static class ExpectedException extends Exception {
        public ExpectedException(String message) {
            super(message);
        }
    }
}
