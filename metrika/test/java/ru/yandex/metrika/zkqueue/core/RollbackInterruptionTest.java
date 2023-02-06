package ru.yandex.metrika.zkqueue.core;

import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicBoolean;

import org.junit.Test;

import ru.yandex.metrika.zkqueue.api.UnitOfWork;

import static org.awaitility.Awaitility.await;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;

/**
 * Check when rollback operation is interrupted, it exits quickly
 */
public final class RollbackInterruptionTest extends BaseCoreTest {

    private static final long IMMEDIATELY_MS = 300;

    @Test
    public void checkRollbackInterruptsImmediately() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx = queue1.newTransaction();
        tx.tryTake(destination1());
        killServer1();

        final AtomicBoolean rollbackWasReturned = new AtomicBoolean();
        final Future<?> rollbackFuture = Executors.newFixedThreadPool(1)
                .submit(() -> {
                    tx.rollback();
                    rollbackWasReturned.set(true);
                }); // Rollback takes a lot of time because server is down

        // Run it for some time
        try {
            rollbackFuture.get(1, TimeUnit.SECONDS); // Our session expiration timeout should allow this
            throw new AssertionError("Rollback should still be running");
        } catch (TimeoutException e) {
            // Good, rollback still runs
        }

        rollbackFuture.cancel(true);
        await().atMost(IMMEDIATELY_MS, TimeUnit.MILLISECONDS).untilTrue(rollbackWasReturned);
    }

}
