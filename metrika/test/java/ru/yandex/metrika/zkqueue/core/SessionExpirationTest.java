package ru.yandex.metrika.zkqueue.core;

import java.util.Optional;

import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;

import ru.yandex.metrika.zkqueue.api.UnitOfWork;
import ru.yandex.metrika.zkqueue.api.exception.ZkQueueIllegalStateException;

import static java.util.concurrent.TimeUnit.MILLISECONDS;
import static org.awaitility.Awaitility.await;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.payload1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.syncTime;

/**
 * Inject session expiration and check all lock nodes are removed.
 */
public final class SessionExpirationTest extends BaseCoreTest {
    @Rule
    public ExpectedException exceptionRule = ExpectedException.none();


    @Test
    public void checkDurability() throws Exception {
        put1(destination1(), payload1());
        expireSession1();
        assertThat(take2(), equalTo(Optional.of(payload1())));
    }

    @Test
    public void checkUnlockingOnSessionClosing() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx = queue1.newTransaction();
        tx.tryTake(destination1()); // Element is locked right now

        expireSession1();

        assertThat(take2(), equalTo(Optional.of(payload1())));
    }

    @Test
    public void checkQueueCantTakeWhenExpired() throws Exception {
        final UnitOfWork tx = queue1.newTransaction();

        expireSession1();

        exceptionRule.expect(Exception.class);
        tx.tryTake(destination1());
    }

    @Test
    public void checkQueueCantPutWhenExpired() throws Exception {
        final UnitOfWork tx = queue1.newTransaction();

        expireSession1();

        await().atMost(syncTime(), MILLISECONDS)
                .until(() -> {
                    try {
                        tx.put(destination1(), payload1());
                        return false;
                    } catch (ZkQueueIllegalStateException ignored) {
                        // wait for exception due to UOW uselessness
                        return true;
                    }
                });
    }

    @Test
    public void checkTxFailsAfterSessionExpiration() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx = queue1.newTransaction();
        tx.tryTake(destination1());

        expireSession1();

        // TX can't commit if lock does not exist
        exceptionRule.expect(Exception.class);
        tx.commit();
    }

    @Test
    public void checkTxFailureWhenOtherWorkerConsumedTheSameZnode() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx1 = queue1.newTransaction();
        tx1.tryTake(destination1());

        expireSession1();

        // Okay, now second client locks this one
        final UnitOfWork tx2 = queue2.newTransaction();
        assertThat(tx2.tryTake(destination1()), equalTo(Optional.of(payload1())));

        // TX1 can't commit because lock was consumed by another tx
        exceptionRule.expect(Exception.class);
        tx1.commit();
    }

    @Test
    public void checkTxWontRollbackOtherTxLocksOnExpiration() throws Exception {
        put1(destination1(), payload1());

        final UnitOfWork tx1 = queue1.newTransaction();
        tx1.tryTake(destination1());

        expireSession1();

        // Okay, now second client locks this one
        final UnitOfWork tx2 = queue2.newTransaction();
        assertThat(tx2.tryTake(destination1()), equalTo(Optional.of(payload1())));

        tx1.rollback();
        tx2.commit();

        assertThat(take1(), equalTo(Optional.empty()));
    }


}
