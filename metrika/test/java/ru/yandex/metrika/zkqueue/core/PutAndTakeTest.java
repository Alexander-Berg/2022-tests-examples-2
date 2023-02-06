package ru.yandex.metrika.zkqueue.core;

import java.util.Optional;

import com.google.common.collect.ImmutableList;
import org.junit.Test;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload2;

/**
 * Base sanity check for queue operations
 */
public final class PutAndTakeTest extends BaseCoreTest {

    @Test
    public void checkPutAndTake() throws Exception {
        put1(destination1(), payload1());
        final Optional<String> result = take1();

        assertThat(result, equalTo(Optional.of(payload1())));
    }

    @Test
    public void checkTakeFromEmptyQueue() throws Exception {
        final Optional<String> result = take1();
        assertThat(result, equalTo(Optional.empty()));
    }

    @Test
    public void checkPutTakeTake() throws Exception {
        put1(destination1(), payload1());
        final Optional<String> first = take1();
        final Optional<String> second = take1();

        assertThat(first, equalTo(Optional.of(payload1())));
        assertThat(second, equalTo(Optional.empty()));
    }

    @Test
    @SuppressWarnings("unchecked")
    public void checkPuttingAndTakingTwice() throws Exception {
        put1(destination1(), payload1());
        put1(destination1(), payload2());

        final Optional<String> first = take1();
        final Optional<String> second = take1();

        assertThat(ImmutableList.of(first, second), containsInAnyOrder(Optional.of(payload1()), Optional.of(payload2())));
    }


}
