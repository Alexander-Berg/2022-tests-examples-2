package ru.yandex.metrika.zkqueue.test;

import java.util.Optional;

import org.apache.curator.RetryPolicy;
import org.apache.curator.retry.RetryForever;

import ru.yandex.metrika.zkqueue.api.DistributedQueue;
import ru.yandex.metrika.zkqueue.api.UnitOfWork;
import ru.yandex.metrika.zkqueue.api.redelivery.ConsumingPolicy;

public final class ZkTesting {

    /**
     * Тестовые среды аркадии часто очень медленные,
     * поэтому берём таймауты с большим запасом
     */
    public static final int SESSION_TIMEOUT = 10000;

    public static final int CONNECTION_TIMEOUT = 1000;

    public static final int SYNC_TIME = 2 * SESSION_TIMEOUT;

    public static int sessionTimeout() {
        return SESSION_TIMEOUT;
    }

    public static int connectionTimeout() {
        return CONNECTION_TIMEOUT;
    }

    public static RetryPolicy retryPolicy() {
        return new RetryForever(connectionTimeout() / 2);
    }

    public static int syncTime() {
        return SYNC_TIME;
    }

    public static String destination1() {
        return "destination-1";
    }

    public static String destination2() {
        return "destination-2";
    }

    public static String payload1() {
        return "Platypus";
    }

    public static String payload2() {
        return "Urchin";
    }

    public static Optional<String> take(DistributedQueue queue, String destination, ConsumingPolicy consumingPolicy) throws Exception {
        try (UnitOfWork tx = queue.newTransaction()) {
            final Optional<String> item = tx.tryTake(destination, consumingPolicy);
            tx.commit();
            return item;
        }
    }
}
