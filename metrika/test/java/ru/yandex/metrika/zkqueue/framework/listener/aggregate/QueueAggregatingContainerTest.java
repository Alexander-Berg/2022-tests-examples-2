package ru.yandex.metrika.zkqueue.framework.listener.aggregate;

import java.util.Arrays;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

import org.hamcrest.Description;
import org.hamcrest.Matchers;
import org.hamcrest.TypeSafeMatcher;
import org.junit.Test;

import ru.yandex.metrika.zkqueue.api.ConsumeTimes;
import ru.yandex.metrika.zkqueue.api.redelivery.ConsumingPolicy;
import ru.yandex.metrika.zkqueue.framework.listener.BaseFrameworkTest;

import static org.awaitility.Awaitility.await;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.metrika.zkqueue.framework.listener.ListenerTimeoutSettings.optimisticSettings;
import static ru.yandex.metrika.zkqueue.framework.listener.aggregate.QueueAggregatingContainerTest.EqualsIgnoringOrder.eq;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.SYNC_TIME;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination2;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.syncTime;

/**
 * Check queue aggregator and make sure policies work as expected
 */
public class QueueAggregatingContainerTest extends BaseFrameworkTest {

    private static final long MINI_DELAY = 1500L;

    private static final ConsumingPolicy consumingPolicy = new ConsumeTimes(10);

    @Test
    public void checkIdentityAggregation() throws Exception {
        final QueueAggregatingContainer container = new QueueAggregatingContainer(queue1, consumingPolicy,
                destination1(), destination2(), new ConstantCombiningPolicy(1), new ConcatCombiner(), optimisticSettings());

        container.start();

        put1(destination1(), payload1());

        await().atMost(syncTime(), TimeUnit.MILLISECONDS)
                .until(() -> take1(destination2()), equalTo(Optional.of(payload1())));

        container.stop();
    }

    @Test
    public void checkConstantAggregation() throws Exception {
        final QueueAggregatingContainer container = new QueueAggregatingContainer(queue1, consumingPolicy,
                destination1(), destination2(), new ConstantCombiningPolicy(2), new ConcatCombiner(), optimisticSettings());

        container.start();

        put1(destination1(), "A");
        put1(destination1(), "B");
        put1(destination1(), "C");

        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .until(() -> take1(destination2()).orElse(""), Matchers.anyOf(eq("AB"), eq("BC"), eq("AC")));

        container.stop();
    }

    @Test
    public void checkTimeoutAggregation() throws Exception {
        final QueueAggregatingContainer container = new QueueAggregatingContainer(queue1, consumingPolicy,
                destination1(), destination2(), new TimestampCombiningPolicy(MINI_DELAY), new ConcatCombiner(), optimisticSettings());

        put1(destination1(), "A");
        put1(destination1(), "B");

        container.start();

        Thread.sleep(2 * MINI_DELAY);

        put1(destination1(), "C");

        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .until(() -> take1(destination2()).orElse(""), eq("AB"));

        container.stop();
    }

    @Test
    public void checkSessionExpirationIsOkForConstantAggregator() throws Exception {
        final QueueAggregatingContainer container = new QueueAggregatingContainer(queue1, consumingPolicy,
                destination1(), destination2(), new ConstantCombiningPolicy(2), new ConcatCombiner(), optimisticSettings());


        container.start();

        put1(destination1(), "A");

        Thread.sleep(MINI_DELAY);

        expireSession1();

        put1(destination1(), "B");

        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .until(() -> take1(destination2()).orElse(""), eq("AB"));

        container.stop();
    }

    @Test
    public void checkServerRestartIsOkForConstantAggregator() throws Exception {
        final QueueAggregatingContainer container = new QueueAggregatingContainer(queue1, consumingPolicy,
                destination1(), destination2(), new ConstantCombiningPolicy(2), new ConcatCombiner(), optimisticSettings());


        container.start();

        put1(destination1(), "A");

        Thread.sleep(MINI_DELAY);

        restartServer1();

        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .ignoreExceptions()
                .until(() ->
                {
                    put1(destination1(), "B");
                    return true;
                });

        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .until(() -> take1(destination2()).orElse(""), eq("AB"));

        container.stop();
    }

    @Test
    public void checkTimeoutAggregatorSurvivesSessionRestart() throws Exception {
        final QueueAggregatingContainer container = new QueueAggregatingContainer(queue1, consumingPolicy,
                destination1(), destination2(), new TimestampCombiningPolicy(MINI_DELAY), new ConcatCombiner(), optimisticSettings());

        container.start();

        put1(destination1(), "A");
        put1(destination1(), "B");

        Thread.sleep(MINI_DELAY);
        expireSession1();

        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .until(() -> take1(destination2()).orElse(""), eq("AB"));

        container.stop();
    }

    @Test
    public void checkTimeoutAggregatorServerDeath() throws Exception {
        final QueueAggregatingContainer container = new QueueAggregatingContainer(queue1, consumingPolicy,
                destination1(), destination2(), new TimestampCombiningPolicy(MINI_DELAY), new ConcatCombiner(), optimisticSettings());

        container.start();

        put1(destination1(), "A");
        put1(destination1(), "B");

        Thread.sleep(MINI_DELAY);
        restartServer1();

        await().atMost(SYNC_TIME, TimeUnit.MILLISECONDS)
                .ignoreExceptions()
                .until(() -> take1(destination2()).orElse(""), eq("AB"));

        container.stop();
    }


    /**
     * Check the strings are anagrams of each other (contain the same letters ignoring order).
     * We use it because our queue can't FIFO right now, so the consuming order is undetermined.
     */
    static class EqualsIgnoringOrder extends TypeSafeMatcher<String> {

        private final String expected;

        static EqualsIgnoringOrder eq(String expected) {
            return new EqualsIgnoringOrder(expected);
        }

        EqualsIgnoringOrder(String expected) {
            this.expected = expected;
        }

        @Override
        protected boolean matchesSafely(String item) {
            return sort(expected).equals(sort(item));
        }

        @Override
        public void describeTo(Description description) {
            description.appendText("a string equals ignoring order with ")
                    .appendValue(expected);
        }

        private String sort(String original) {
            final char[] sorted = Arrays.copyOf(original.toCharArray(), original.length());
            Arrays.sort(sorted);
            return new String(sorted);
        }
    }


}
